"""028: "Is this a business?" Part 1 in Blender. Builds the whole scene and bakes every frame.

Run inside Blender (5.3, EEVEE) with BASE pointing at a folder that holds anim028.py + part1.json:
    BASE = "~/Movies/spare-pixels-blender/028"; exec(open(BASE + "/build028.py").read())
Everything that moves comes from anim028.py (a 1:1 port of the 2D original's timing and paths).
"""
import bpy, bmesh, math, json, os, types, random
from mathutils import Vector

BASE = os.path.expanduser(globals().get("BASE", "~/Movies/spare-pixels-blender/028"))
A = types.ModuleType("anim028")
A.__dict__["__file__"] = os.path.join(BASE, "anim028.py")
exec(open(os.path.join(BASE, "anim028.py")).read(), A.__dict__)
FPS, N, T = A.FPS, A.N, A.T
R = random.Random(28)


# ------------------------------------------------------------------ utilities
def hexlin(h):
    h = A.C.get(h, h).lstrip("#")
    out = []
    for i in (0, 2, 4):
        v = int(h[i:i + 2], 16) / 255
        out.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
    return tuple(out)


def clear_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras, bpy.data.actions,
                 bpy.data.curves):
        for d in list(coll):
            if d.users == 0:
                coll.remove(d)


_M = {}


def mat(name, base=(0.5, 0.5, 0.5), rough=0.5, coat=0.0, emit=None, estr=0.0, metal=0.0, sss=0.0, sheen=0.0,
        alpha=1.0, trans=0.0):
    if name in _M:
        return _M[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*base, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Subsurface Weight"].default_value = sss
    b.inputs["Sheen Weight"].default_value = sheen
    b.inputs["Transmission Weight"].default_value = trans
    if emit is not None:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = estr
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = "BLENDED"
        except Exception:
            pass
    _M[name] = m
    return m


def cmat(cname, rough=0.75, sheen=0.4):
    """cloth / plastic in a palette colour"""
    return mat("cloth_" + cname, hexlin(cname), rough, sheen=sheen)


def tex_mat(name, kind, c1, c2, scale=1.0, rough=0.6, bump=0.15, extra=None):
    """procedural materials: noise / wave (wood) / brick / checker"""
    if name in _M:
        return _M[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = extra.get("mscale", (scale, scale, scale)) if extra else (scale, scale, scale)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*c1, 1)
    ramp.color_ramp.elements[1].color = (*c2, 1)
    if kind == "noise":
        tx = nt.nodes.new("ShaderNodeTexNoise"); tx.inputs["Scale"].default_value = 6.0
        tx.inputs["Detail"].default_value = 8.0
        nt.links.new(mp.outputs[0], tx.inputs["Vector"]); nt.links.new(tx.outputs["Fac"], ramp.inputs[0])
    elif kind == "wood":
        tx = nt.nodes.new("ShaderNodeTexWave"); tx.wave_type = "BANDS"; tx.bands_direction = "X"
        tx.inputs["Scale"].default_value = 3.0; tx.inputs["Distortion"].default_value = 7.0
        tx.inputs["Detail"].default_value = 3.0
        nt.links.new(mp.outputs[0], tx.inputs["Vector"]); nt.links.new(tx.outputs["Fac"], ramp.inputs[0])
    elif kind == "brick":
        tx = nt.nodes.new("ShaderNodeTexBrick")
        tx.inputs["Color1"].default_value = (*c1, 1); tx.inputs["Color2"].default_value = (*c2, 1)
        tx.inputs["Mortar"].default_value = (*[0.55, 0.52, 0.48], 1)
        tx.inputs["Scale"].default_value = 1.0; tx.inputs["Mortar Size"].default_value = 0.012
        tx.inputs["Brick Width"].default_value = 0.25; tx.inputs["Row Height"].default_value = 0.075
        nt.links.new(mp.outputs[0], tx.inputs["Vector"]); nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
        tx2 = tx
    elif kind == "checker":
        tx = nt.nodes.new("ShaderNodeTexChecker"); tx.inputs["Scale"].default_value = 1.0
        tx.inputs["Color1"].default_value = (*c1, 1); tx.inputs["Color2"].default_value = (*c2, 1)
        nt.links.new(mp.outputs[0], tx.inputs["Vector"]); nt.links.new(tx.outputs["Color"], b.inputs["Base Color"])
    if kind in ("noise", "wood"):
        nt.links.new(ramp.outputs[0], b.inputs["Base Color"])
    if bump:
        bn = nt.nodes.new("ShaderNodeBump"); bn.inputs["Strength"].default_value = bump
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 40.0
        nt.links.new(mp.outputs[0], nz.inputs["Vector"]); nt.links.new(nz.outputs["Fac"], bn.inputs["Height"])
        nt.links.new(bn.outputs["Normal"], b.inputs["Normal"])
    _M[name] = m
    return m


COL = None


def obj(name, data, mats=(), loc=(0, 0, 0), rot=(0, 0, 0), scl=(1, 1, 1), parent=None):
    o = bpy.data.objects.new(name, data)
    COL.objects.link(o)
    if data is not None and hasattr(data, "materials"):
        for m_ in mats:
            data.materials.append(m_)
    o.location, o.rotation_euler, o.scale = loc, rot, scl
    if parent:
        o.parent = parent
    return o


def empty(name, loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    return obj(name, None, loc=loc, parent=parent, rot=rot)


def box_mesh(name, sx, sy, sz, bevel=0.0, seg=2, center=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=bm.verts)
    bmesh.ops.translate(bm, vec=center, verts=bm.verts)
    if bevel:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=seg, profile=0.5, affect="EDGES")
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = bevel > 0
    return me


def box(name, x0, x1, y0, y1, z0, z1, mats, bevel=0.0, parent=None):
    me = box_mesh(name, x1 - x0, y1 - y0, z1 - z0, bevel)
    return obj(name, me, mats, loc=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), parent=parent)


def by_normal(o, front_idx=1, top_idx=None, bottom_idx=None):
    for p in o.data.polygons:
        if p.normal.y < -0.9:
            p.material_index = front_idx
        elif top_idx is not None and p.normal.z > 0.9:
            p.material_index = top_idx
        elif bottom_idx is not None and p.normal.z < -0.9:
            p.material_index = bottom_idx


def cyl_mesh(name, r, h, verts=24, r2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts, radius1=r,
                          radius2=r if r2 is None else r2, depth=h)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return me


def sphere_mesh(name, r=1.0, seg=24, rings=16):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=r)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return me


def ico_mesh(name, r=1.0, sub=2):
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return me


def capsule_mesh(name, r, length, seg=16):
    """capsule from z=0 down to z=-length (pivot at the top)"""
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=12, radius=r)
    for v in bm.verts:
        if v.co.z < 0:
            v.co.z -= (length - 2 * r)
        v.co.z -= r
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return me


def stroke(name, pts, depth, mats, parent=None, loc=(0, 0, 0)):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"; cu.bevel_depth = depth; cu.bevel_resolution = 3; cu.use_fill_caps = True
    sp = cu.splines.new("POLY"); sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts):
        p.co = (*c, 1)
    return obj(name, cu, mats, loc=loc, parent=parent)


_FONTS = {}


def font(fname):
    if fname not in _FONTS:
        f = os.path.join(BASE, "fonts", fname)
        _FONTS[fname] = bpy.data.fonts.load(f, check_existing=True) if os.path.exists(f) else None
    return _FONTS[fname]


def text(name, body, size, mats, loc, rot=(math.pi / 2, 0, 0), parent=None, extrude=0.004, align="CENTER", fname="Inter-Black.ttf"):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body; cu.size = size; cu.extrude = extrude; cu.align_x = align; cu.align_y = "CENTER"
    if font(fname):
        cu.font = font(fname)
    return obj(name, cu, mats, loc=loc, rot=rot, parent=parent)


# ------------------------------------------------------------------ keys (Blender 5 slotted actions)
def fcurve_of(idd, path, index):
    ad = idd.animation_data
    act = ad.action
    if hasattr(act, "fcurves"):
        try:
            fc = act.fcurves.find(path, index=index)
            if fc:
                return fc
        except Exception:
            pass
    from bpy_extras import anim_utils
    return anim_utils.action_get_channelbag_for_slot(act, ad.action_slot).fcurves.find(path, index=index)


def keys(idd, path, index, frames, values, interp="LINEAR"):
    if not frames:
        return
    owner, attr = (idd.path_resolve(path.rsplit(".", 1)[0]), path.rsplit(".", 1)[1]) if "." in path else (idd, path)
    prop = getattr(owner, attr)
    if index is None:
        setattr(owner, attr, values[0])
        idd.keyframe_insert(path, frame=frames[0])
        fc = fcurve_of(idd, path, 0)
    else:
        prop[index] = values[0]
        idd.keyframe_insert(path, index=index, frame=frames[0])
        fc = fcurve_of(idd, path, index)
    kp = fc.keyframe_points
    if len(frames) > 1:
        kp.add(len(frames) - 1)
    co = []
    for f, v in zip(frames, values):
        co += [f, v]
    kp.foreach_set("co", co)
    for p in kp:
        p.interpolation = interp
    fc.update()


def changes(frames, values, eps=1e-6):
    fs, vs, last = [], [], None
    for f, v in zip(frames, values):
        if last is None or abs(v - last) > eps:
            fs.append(f); vs.append(v); last = v
    return fs, vs


def unwrap(vals):
    out = [vals[0]]
    for v in vals[1:]:
        out.append(v + 2 * math.pi * round((out[-1] - v) / (2 * math.pi)))
    return out


def vis_keys(o, frames, flags):
    """show/hide by scale (works with motion blur, no render-visibility flicker)"""
    s0 = tuple(o.scale)
    f_, v_ = changes(frames, [1.0 if f else 0.0 for f in flags])
    for i in range(3):
        keys(o, "scale", i, f_, [s0[i] * max(v, 1e-4) for v in v_], "CONSTANT")


# ------------------------------------------------------------------ scene settings
def setup_render():
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 0, N - 1
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1920, 100
    ee = sc.eevee
    for k, v in dict(taa_render_samples=32, taa_samples=16, use_raytracing=True, bokeh_max_size=120.0,
                     use_shadows=True, shadow_ray_count=2, shadow_step_count=8, use_fast_gi=True).items():
        try:
            setattr(ee, k, v)
        except Exception as e:
            print("eevee setting skipped:", k, e)
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = 0.5
    try:
        sc.render.motion_blur_position = "START"
    except Exception:
        pass
    sc.view_settings.view_transform = "AgX"
    for look in ("AgX - Punchy", "Punchy", "None"):
        try:
            sc.view_settings.look = look
            break
        except Exception:
            pass
    sc.view_settings.exposure = 0.15
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 95
    sc.render.filepath = os.path.join(BASE, "frames", "f_")
    w = sc.world or bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    bg = nt.nodes.get("Background")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.45
    ramp.color_ramp.elements[0].color = (*hexlin("#F4E3CC"), 1)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (*hexlin("#9FC3E6"), 1)
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = -0.2; mr.inputs["From Max"].default_value = 0.6
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(tc.outputs["Window"], sep.inputs[0])
    nt.links.new(sep.outputs["Y"], mr.inputs["Value"])
    nt.links.new(mr.outputs["Result"], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], bg.inputs[0])
    bg.inputs[1].default_value = 0.9


# ------------------------------------------------------------------ the house
def build_house():
    Z, X0, X1, D = A.Z, A.HOUSE_X0, A.HOUSE_X1, A.DEPTH
    plaster = tex_mat("plaster", "noise", hexlin("#EDE3D2"), hexlin("#E2D5BF"), scale=0.6, rough=0.85, bump=0.08)
    plaster_b = tex_mat("plaster_b", "noise", hexlin("#D9CDB7"), hexlin("#CDBFA6"), scale=0.6, rough=0.9, bump=0.1)
    wood = tex_mat("wood", "wood", hexlin("#B98A5A"), hexlin("#8F6439"), scale=1.4, rough=0.45, bump=0.05)
    stairwood = tex_mat("stairwood", "wood", hexlin("#C99A66"), hexlin("#A0703F"), scale=2.0, rough=0.5, bump=0.05)
    concrete = tex_mat("concrete", "noise", hexlin("#A9A39A"), hexlin("#8F8980"), scale=1.5, rough=0.9, bump=0.3)
    tiles = tex_mat("tiles", "checker", hexlin("#CFC6B6"), hexlin("#B7AC98"), scale=1.6, rough=0.35, bump=0.0,
                    extra={"mscale": (1.6, 1.6, 1.6)})
    navy = mat("slabcut", hexlin("navy"), 0.55)
    ceiling = mat("ceiling", hexlin("#F4EEE4"), 0.9)
    brick = tex_mat("brick", "brick", hexlin("#B56A4C"), hexlin("#9E5A40"), scale=1.0, rough=0.85, bump=0.2)
    earth = tex_mat("earth", "noise", hexlin("#8B6A4A"), hexlin("#6E5238"), scale=0.5, rough=0.95, bump=0.4)
    grass = tex_mat("grass", "noise", hexlin("#6FA35A"), hexlin("#4F8443"), scale=2.0, rough=0.9, bump=0.3)
    metal = mat("railing", hexlin("#2C2F38"), 0.35, metal=0.8)

    # slabs: floor 4..0 with a hole over the flight going down from them; basement floor; roof
    for k in range(5):
        xs, xe = (A.SA, A.SB) if k % 2 == 0 else (A.SB, A.SA)
        hx0, hx1 = A.X(min(xs, xe)) - 0.05, A.X(max(xs, xe)) + 0.05
        hy0, hy1 = A.Y_STAIR - A.STAIR_W / 2 - 0.08, A.Y_STAIR + A.STAIR_W / 2 + 0.08
        z0, z1 = Z[k] - 0.24, Z[k]
        parts = [(X0, hx0, 0, D), (hx1, X1, 0, D), (hx0, hx1, 0, hy0), (hx0, hx1, hy1, D)]
        for j, (a, b, c, d) in enumerate(parts):
            o = box(f"Slab{k}_{j}", a, b, c, d, z0, z1, [wood, navy, ceiling])
            by_normal(o, front_idx=1, top_idx=0, bottom_idx=2)
            for p in o.data.polygons:
                if abs(p.normal.x) > 0.9 or abs(p.normal.y) > 0.9 and p.normal.y > 0:
                    p.material_index = 1
    o = box("SlabB", X0, X1, 0, D, -0.3, 0.0, [tiles, navy, concrete]); by_normal(o, 1, 0, 2)
    o = box("Roof", X0 - 0.3, X1 + 0.3, 0, D + 0.3, Z[0] + A.FH - 0.05, Z[0] + A.FH + 0.3, [concrete, navy, ceiling])
    by_normal(o, 1, 0, 2)
    box("Parapet", X0 - 0.3, X1 + 0.3, D + 0.05, D + 0.3, Z[0] + A.FH + 0.3, Z[0] + A.FH + 0.75, [concrete])
    box("RoofBox", -0.6, 0.4, 1.6, 2.8, Z[0] + A.FH + 0.3, Z[0] + A.FH + 1.3, [brick], bevel=0.03)
    # back walls: plaster upstairs, concrete in the basement
    box("BackWallB", X0, X1, D, D + 0.25, -0.3, Z[4], [concrete])
    box("BackWall", X0, X1, D, D + 0.25, Z[4], Z[0] + A.FH, [plaster])
    # side walls: brick outside, cut face navy at the front
    for side, (a, b) in (("L", (X0 - 0.3, X0)), ("R", (X1, X1 + 0.3))):
        o = box(f"Side{side}", a, b, 0, D + 0.25, -0.3, Z[0] + A.FH, [brick, navy]); by_normal(o, 1)
    # stairs: 16 steps per flight + stringer + front railing
    for k in range(5):
        xs, xe = (A.SA, A.SB) if k % 2 == 0 else (A.SB, A.SA)
        x0, x1, z0, z1 = A.X(xs), A.X(xe), Z[k], Z[k + 1]
        n = 16
        run, rise = (x1 - x0) / n, (z1 - z0) / n
        y0, y1 = A.Y_STAIR - A.STAIR_W / 2, A.Y_STAIR + A.STAIR_W / 2
        bm = bmesh.new()
        for i in range(n):
            ax, bx = sorted((x0 + run * i, x0 + run * (i + 1)))
            top = z0 + rise * (i + 1)
            res = bmesh.ops.create_cube(bm, size=1.0)
            vs = res["verts"]
            bmesh.ops.scale(bm, vec=(bx - ax + 0.02, y1 - y0, 0.06), verts=vs)
            bmesh.ops.translate(bm, vec=((ax + bx) / 2, (y0 + y1) / 2, top - 0.03), verts=vs)
        me = bpy.data.meshes.new(f"Treads{k}"); bm.to_mesh(me); bm.free()
        obj(f"Treads{k}", me, [stairwood])
        # stringer (inclined slab under the treads)
        L = math.hypot(x1 - x0, z1 - z0)
        ang = math.atan2(z1 - z0, x1 - x0)
        st = obj(f"Stringer{k}", box_mesh(f"Str{k}", L, A.STAIR_W - 0.04, 0.18), [plaster_b, navy],
                 loc=((x0 + x1) / 2, A.Y_STAIR, (z0 + z1) / 2 - 0.16), rot=(0, -ang, 0))
        by_normal(st, 1)
        # railing on the open (front) side
        yr = y0 + 0.04
        for i in range(0, n + 1, 4):
            px, pz = x0 + run * i, z0 + rise * i
            obj(f"Post{k}_{i}", cyl_mesh(f"P{k}{i}", 0.018, 0.92, 10), [metal], loc=(px, yr, pz + 0.46))
        stroke(f"Rail{k}", [(x0, yr, z0 + 0.92), (x1, yr, z1 + 0.92)], 0.022, [metal])
        stroke(f"RailMid{k}", [(x0, yr, z0 + 0.5), (x1, yr, z1 + 0.5)], 0.01, [metal])

    # earth + grass outside, earth under the basement
    box("EarthL", -60, X0 - 0.3, -2, 30, -45, Z[4], [earth, earth])
    box("EarthR", X1 + 0.3, 60, -2, 30, -45, Z[4], [earth, earth])
    box("EarthU", X0 - 0.3, X1 + 0.3, -2, 30, -45, -0.3, [earth])
    box("EarthBack", X0 - 0.3, X1 + 0.3, D + 0.25, 30, -0.3, Z[4], [earth])
    box("GrassL", -60, X0 - 0.3, -2, 30, Z[4], Z[4] + 0.08, [grass])
    box("GrassR", X1 + 0.3, 60, -2, 30, Z[4], Z[4] + 0.08, [grass])
    box("GrassBack", X0 - 0.3, X1 + 0.3, D + 0.25, 30, Z[4], Z[4] + 0.08, [grass])
    # a few stones in the earth cross-section
    stone = mat("stone", hexlin("#7D7468"), 0.8)
    bands = [(Z[4] - 0.55, Z[4] + 0.001, "#6A4A31"), (-4.6, -4.0, "#9C8F80"), (-9.6, -9.0, "#A0705A"), (-45, -14.5, "#5E4632")]
    for j, (z0, z1, c) in enumerate(bands):
        m_ = tex_mat(f"band{j}", "noise", hexlin(c), tuple(v * 0.8 for v in hexlin(c)), 0.7, 0.95, 0.3)
        if z1 <= -0.3:
            box(f"Band{j}", -60, 60, -2.03, -1.99, z0, z1, [m_])
        else:
            box(f"BandL{j}", -60, X0 - 0.3, -2.03, -1.99, z0, z1, [m_])
            box(f"BandR{j}", X1 + 0.3, 60, -2.03, -1.99, z0, z1, [m_])
    for i in range(70):
        x = R.uniform(-16, 16)
        top = (Z[4] - 0.7) if (x < X0 - 0.5 or x > X1 + 0.5) else -0.6
        z = R.uniform(-16, top)
        if -4.7 < z < -3.9:
            continue
        s = R.uniform(0.08, 0.3)
        obj(f"Stone{i}", ico_mesh(f"St{i}", 1, 2), [stone], loc=(x, -2.0, z), scl=(s * 1.5, s, s), rot=(0, R.uniform(-0.5, 0.5), 0))
    for i in range(120):
        x = R.uniform(-16, 16)
        s = R.uniform(0.04, 0.09)
        obj(f"Gravel{i}", ico_mesh("Gr", 1, 1), [stone], loc=(x, -2.0, R.uniform(-4.55, -4.05)), scl=(s * 1.3, s, s))
    # foundation footing under the house
    box("Footing", X0 - 0.6, X1 + 0.6, -2.02, D + 0.3, -0.75, -0.3, [concrete])
    # trees and bushes beside the house
    bark = mat("bark", hexlin("#6B4B32"), 0.9)
    leaf = tex_mat("leaf", "noise", hexlin("#6E9E55"), hexlin("#4C7A3E"), scale=3.0, rough=0.8, bump=0.4)
    for tx, ty, h in ((-10.2, 3.5, 6.5), (10.6, 4.5, 7.5), (-13.5, 9, 8.0), (14.0, 10, 6.0)):
        obj("Trunk", cyl_mesh("Tr", 0.22, h * 0.55, 12, 0.16), [bark], loc=(tx, ty, Z[4] + h * 0.27))
        for j in range(6):
            r = R.uniform(1.2, 1.9) * h / 7
            obj("Leaf", ico_mesh("Lf", 1, 2), [leaf], loc=(tx + R.uniform(-1, 1) * r, ty + R.uniform(-0.6, 0.6) * r,
                                                         Z[4] + h * 0.62 + R.uniform(-0.4, 0.8) * r), scl=(r, r, r * 0.9))
    for i in range(10):
        x = R.choice([R.uniform(-15, -8.2), R.uniform(8.2, 15)])
        r = R.uniform(0.4, 0.8)
        obj("Bush", ico_mesh("Bu", 1, 2), [leaf], loc=(x, R.uniform(0.6, 3), Z[4] + r * 0.6), scl=(r * 1.3, r, r))
    # far skyline (haze)
    haze = mat("haze", hexlin("#AFC2D6"), 1.0)
    for i in range(16):
        w, h = R.uniform(6, 14), R.uniform(14, 34)
        x = -60 + i * 8 + R.uniform(-2, 2)
        box(f"City{i}", x - w / 2, x + w / 2, 70, 76, 0, h, [haze])

    # doors, mats, floor numbers, lamps, props
    door_m = tex_mat("doorwood", "wood", hexlin("#9C7148"), hexlin("#7E5634"), scale=2.0, rough=0.5, bump=0.03)
    door_j = tex_mat("doorjonas", "wood", hexlin("#E7B54A"), hexlin("#C9932E"), scale=2.0, rough=0.45, bump=0.03)
    frame_m = mat("doorframe", hexlin("#F7F2EA"), 0.5)
    brass = mat("brass", hexlin("#C9A24A"), 0.3, metal=1.0)
    ink = mat("ink", hexlin("navy"), 0.6)
    matm = mat("doormat", hexlin("#6E5A48"), 1.0)
    pot = mat("pot", hexlin("#C46A4A"), 0.7)
    labels = ["4", "3", "2", "1", "0", "-1"]
    for k in range(5):
        z = Z[k]
        for side, xpx in (("A", A.DOOR_L), ("B", A.DOOR_R)):
            x = A.X(xpx)
            box(f"Frame{k}{side}", x - 0.55, x + 0.55, D - 0.06, D, z, z + 2.2, [frame_m])
            dm = door_j if (k == 0 and side == "A") else door_m
            box(f"Door{k}{side}", x - 0.46, x + 0.46, D - 0.1, D - 0.05, z, z + 2.08, [dm], bevel=0.01)
            obj(f"Knob{k}{side}", sphere_mesh("Kn", 0.035, 12, 8), [brass], loc=(x + (0.33 if side == "A" else -0.33), D - 0.13, z + 1.0))
            text(f"Num{k}{side}", f"{labels[k]}{side}", 0.12, [brass], loc=(x, D - 0.11, z + 1.75))
            box(f"Mat{k}{side}", x - 0.4, x + 0.4, D - 0.75, D - 0.12, z, z + 0.02, [matm])
        text(f"Floor{k}", labels[k], 0.75, [ink], loc=(-1.2, D - 0.02, z + 1.55), extrude=0.003)
        # framed pictures, shoes, umbrella stand
        for j, (fx, c) in enumerate(((-4.2, ["sky", "coral", "teal", "gold", "lilac"][k]), (2.4, ["pink", "green", "sky", "coral", "gold"][k]))):
            if k == 4 and j == 1:
                continue
            box(f"PicFrame{k}{j}", fx - 0.36, fx + 0.36, D - 0.04, D, z + 1.25, z + 1.8, [frame_m])
            box(f"Pic{k}{j}", fx - 0.3, fx + 0.3, D - 0.05, D - 0.03, z + 1.31, z + 1.74, [cmat(c, 0.5, 0.0)])
            obj(f"PicSun{k}{j}", cyl_mesh("PS", 0.07, 0.01, 20), [cmat("white", 0.5, 0.0)], loc=(fx + 0.12, D - 0.06, z + 1.6), rot=(math.pi / 2, 0, 0))
        for side, xpx in (("A", A.DOOR_L), ("B", A.DOOR_R)):
            x = A.X(xpx)
            if R.random() < 0.75:
                sc_ = R.choice(["coral", "navy", "white", "teal", "gold"])
                for dx in (-0.08, 0.08):
                    box(f"Shoe{k}{side}{dx}", x + 0.15 + dx - 0.05, x + 0.15 + dx + 0.05, D - 0.62, D - 0.38, z + 0.02, z + 0.1, [cmat(sc_, 0.5, 0.0)], bevel=0.02)
        if k in (1, 3):
            obj(f"Umb{k}", cyl_mesh("Um", 0.12, 0.5, 20), [mat("umbstand", hexlin("#4F6E8A"), 0.3, metal=0.5)], loc=(6.9, 2.95, z + 0.25))
            for j, c in enumerate(["coral", "navy"]):
                stroke(f"Umbrella{k}{j}", [(6.85 + j * 0.08, 2.95, z + 0.2), (6.82 + j * 0.1, 2.95, z + 0.95)], 0.025, [cmat(c, 0.5, 0.0)])
        # ceiling lamp + warm light
        for lx in (-3.6, 3.4):
            obj(f"LampCord{k}{lx}", cyl_mesh("LC", 0.006, 0.35, 6), [ink], loc=(lx, 2.1, z + A.FH - 0.42))
            shade = obj(f"Shade{k}{lx}", cyl_mesh("Sh", 0.05, 0.12, 20, 0.16), [mat("shade", hexlin("#F3E9D6"), 0.6)],
                        loc=(lx, 2.1, z + A.FH - 0.62))
            bulb = obj(f"Bulb{k}{lx}", sphere_mesh("Bb", 0.045, 12, 8), [mat("bulb", (1, 0.9, 0.7), 0.2, emit=(1, 0.85, 0.6), estr=8)],
                       loc=(lx, 2.1, z + A.FH - 0.7))
            L = bpy.data.lights.new(f"Lamp{k}{lx}", "POINT"); L.energy = 140; L.color = (1.0, 0.82, 0.62)
            L.shadow_soft_size = 0.15
            obj(f"LampL{k}{lx}", L, loc=(lx, 2.0, z + A.FH - 0.8))
        # a plant by the wall on alternate floors, mailboxes on the ground floor
        if k % 2 == 1:
            obj(f"Pot{k}", cyl_mesh("Po", 0.18, 0.35, 20, 0.14), [pot], loc=(-6.9, 2.9, z + 0.175))
            for j in range(4):
                r = R.uniform(0.18, 0.28)
                obj(f"Plant{k}{j}", ico_mesh("Pl", 1, 2), [leaf], loc=(-6.9 + R.uniform(-0.12, 0.12), 2.9 + R.uniform(-0.1, 0.1),
                                                                       z + 0.55 + R.uniform(0, 0.35)), scl=(r, r, r * 1.2))
    for j in range(5):
        box(f"Mailbox{j}", 1.0 + j * 0.42, 1.38 + j * 0.42, D - 0.22, D - 0.02, Z[4] + 1.05, Z[4] + 1.45,
            [mat("mailbox", hexlin("#4F6E8A"), 0.4, metal=0.5)], bevel=0.01)
    text("FloorB", labels[5], 0.75, [ink], loc=(-1.2, D - 0.02, Z[5] + 1.55), extrude=0.003)

    # basement: high window, pipes, bulb, shelf, clock
    glass = mat("winglass", hexlin("#CFE6F5"), 0.05, emit=hexlin("#CFE6F5"), estr=1.5)
    box("Window", -4.6, -2.8, D - 0.04, D + 0.02, 1.85, 2.4, [glass])
    box("WinFrame", -4.7, -2.7, D - 0.06, D - 0.03, 1.78, 2.47, [frame_m])
    WL = bpy.data.lights.new("WinLight", "AREA"); WL.shape = "RECTANGLE"; WL.size = 1.7; WL.size_y = 0.5
    WL.energy = 120; WL.color = (0.78, 0.88, 1.0)
    obj("WinLightO", WL, loc=(-3.7, D - 0.1, 2.1), rot=(math.radians(-75), 0, 0))
    pipe = mat("pipe", hexlin("#9AA0A6"), 0.3, metal=0.9)
    p = obj("PipeH", cyl_mesh("PH", 0.05, 14.4, 16), [pipe], loc=(0, D - 0.12, 2.35), rot=(0, math.pi / 2, 0))
    obj("PipeV", cyl_mesh("PV", 0.045, 2.35, 16), [pipe], loc=(7.0, D - 0.12, 1.18))
    obj("PipeV2", cyl_mesh("PV2", 0.035, 2.35, 16), [pipe], loc=(-6.4, D - 0.12, 1.18))
    obj("BBulbCord", cyl_mesh("BC", 0.006, 0.4, 6), [ink], loc=(4.6, 2.2, 2.38))
    obj("BBulb", sphere_mesh("BB", 0.05, 12, 8), [mat("bulb2", (1, 0.9, 0.7), 0.2, emit=(1, 0.85, 0.6), estr=10)], loc=(4.6, 2.2, 2.15))
    L = bpy.data.lights.new("BasementBulb", "POINT"); L.energy = 160; L.color = (1.0, 0.8, 0.58); L.shadow_soft_size = 0.08
    obj("BasementBulbL", L, loc=(4.6, 2.1, 2.05))
    shelf = mat("shelf", hexlin("#A58258"), 0.6)
    box("Shelf", 5.95, 6.95, D - 0.3, D - 0.02, 1.5, 1.55, [shelf])
    for j, c in enumerate(["teal", "coral", "white", "sky"]):
        obj(f"Bottle{j}", cyl_mesh("Bt", 0.07, 0.26, 16), [cmat(c, 0.35, 0.0)], loc=(6.1 + j * 0.24, D - 0.16, 1.68))
    for j, c in enumerate(["white", "sky", "white"]):
        box(f"Towel{j}", 6.05 + j * 0.0, 6.45, D - 0.28, D - 0.05, 1.55 + j * 0.07, 1.62 + j * 0.07, [cmat(c, 0.95, 0.8)], bevel=0.02)
    # cork board with notes (no text) left of where Jonas stands
    box("Cork", 3.55, 4.25, D - 0.05, D - 0.01, 1.25, 1.8, [tex_mat("cork", "noise", hexlin("#B88A5A"), hexlin("#9C7247"), 4.0, 0.9, 0.3)])
    for j, (cx, cz, c) in enumerate([(3.72, 1.62, "#FFF6C8"), (3.98, 1.66, "#FBF8F2"), (4.1, 1.4, "#F7D9E4"), (3.75, 1.38, "#DCEBF7")]):
        box(f"Paper{j}", cx - 0.1, cx + 0.1, D - 0.06, D - 0.05, cz - 0.12, cz + 0.12, [mat("paper" + str(j), hexlin(c), 0.8)]).rotation_euler = (0, R.uniform(-0.12, 0.12), 0)
        obj(f"Pin{j}", sphere_mesh("Pn", 0.012, 8, 6), [cmat(["coral", "teal", "gold", "navy"][j], 0.3, 0.0)], loc=(cx, D - 0.07, cz + 0.09))
    # laundry basket stack + a drying rack on the far left of the basement
    rack = mat("rack", hexlin("#D8DCE2"), 0.3, metal=0.6)
    for j in range(5):
        stroke(f"RackBar{j}", [(-6.2, 1.8 + j * 0.18, 0.95), (-4.8, 1.8 + j * 0.18, 0.95)], 0.008, [rack])
    for lx in (-6.2, -4.8):
        stroke(f"RackLeg{lx}", [(lx, 1.7, 0), (lx, 2.25, 0.95), (lx, 2.7, 0)], 0.012, [rack])
    for j, c in enumerate(["sky", "white", "coral", "white", "lilac"]):
        box(f"Hang{j}", -6.0 + j * 0.26, -5.82 + j * 0.26, 1.78 + (j % 3) * 0.18, 1.8 + (j % 3) * 0.18, 0.5, 0.95, [cmat(c, 0.95, 0.7)])
    box("Bench", -1.6, 0.4, D - 0.5, D - 0.05, 0.42, 0.48, [wood])
    for lx in (-1.45, 0.25):
        box(f"BenchLeg{lx}", lx - 0.04, lx + 0.04, D - 0.45, D - 0.1, 0, 0.42, [metal])


def build_clock():
    c = empty("Clock", loc=(5.5, A.DEPTH - 0.04, 1.95))
    face = obj("ClockFace", cyl_mesh("CF", 0.2, 0.04, 40), [mat("clockface", hexlin("#FBF8F2"), 0.4)], rot=(math.pi / 2, 0, 0), parent=c)
    obj("ClockRim", cyl_mesh("CR", 0.22, 0.05, 40), [mat("clockrim", hexlin("navy"), 0.4)], loc=(0, 0.01, 0), rot=(math.pi / 2, 0, 0), parent=c)
    ink = mat("ink2", hexlin("ink"), 0.5)
    for i in range(12):
        a = i * math.pi / 6
        box(f"Tick{i}", -0.006, 0.006, -0.03, -0.022, 0.16, 0.19, [ink], parent=c).rotation_euler = (0, a, 0)
    mh = empty("MinHand", loc=(0, -0.03, 0), parent=c)
    box("MinHandM", -0.008, 0.008, -0.005, 0.005, 0, 0.17, [ink], parent=mh)
    hh = empty("HourHand", loc=(0, -0.035, 0), parent=c)
    box("HourHandM", -0.011, 0.011, -0.005, 0.005, 0, 0.11, [ink], parent=hh)
    hh.rotation_euler = (0, math.radians(10 * 30), 0)
    return mh, hh


# ------------------------------------------------------------------ laundry blobs and baskets
def blob(name, color, scale, parent, loc, seed):
    rr = random.Random(seed)
    o = obj(name, ico_mesh("Bl", 1, 2), [cmat(color)], loc=loc, parent=parent,
            scl=(scale * rr.uniform(1.0, 1.5), scale * rr.uniform(0.8, 1.2), scale * rr.uniform(0.55, 0.8)),
            rot=(rr.uniform(-0.4, 0.4), rr.uniform(-0.4, 0.4), rr.uniform(0, 3)))
    return o


def basket(name, parent, colors, loc=(0, 0, 0)):
    """open laundry basket (teal plastic) + clothes heap. returns (root, heap_root)"""
    root = empty(name, loc=loc, parent=parent)
    plast = mat("basket", hexlin("#2F8F89"), 0.45, coat=0.2)
    w, d, h, t = 0.52, 0.36, 0.26, 0.02
    box(name + "_b", -w / 2, w / 2, -d / 2, d / 2, 0, t, [plast], parent=root)
    for nm, (a, b, c, e) in {"f": (-w / 2, w / 2, -d / 2, -d / 2 + t), "k": (-w / 2, w / 2, d / 2 - t, d / 2),
                             "l": (-w / 2, -w / 2 + t, -d / 2, d / 2), "r": (w / 2 - t, w / 2, -d / 2, d / 2)}.items():
        box(name + "_" + nm, a, b, c, e, 0, h, [plast], bevel=0.006, parent=root)
    heap = empty(name + "_heap", parent=root)
    for i, col in enumerate(colors):
        blob(f"{name}_c{i}", col, 0.1, heap, ((i % 3 - 1) * 0.14, (i // 3 - 0.5) * 0.12, h * 0.75 + (i % 2) * 0.04), hash(name) % 1000 + i)
    return root, heap


# ------------------------------------------------------------------ the washer
def build_washer():
    wx, wy, wz = A.WASHER
    root = empty("Washer", loc=(wx, wy, 0))
    shake = empty("WasherShake", loc=(0, 0, 0), parent=root)
    enamel = mat("enamel", hexlin("#F4F2EE"), 0.22, coat=0.6)
    chrome = mat("chrome", (0.8, 0.8, 0.82), 0.12, metal=1.0)
    darkglass = mat("darkglass", hexlin("#24314A"), 0.04, coat=1.0)
    box("WBody", -0.3, 0.3, -0.3, 0.3, 0.03, 0.86, [enamel], bevel=0.03, parent=shake)
    box("WPanel", -0.3, 0.3, -0.31, -0.25, 0.72, 0.86, [mat("panel", hexlin("#E6E3DE"), 0.3)], bevel=0.01, parent=shake)
    box("WDrawer", -0.27, -0.08, -0.315, -0.29, 0.75, 0.83, [enamel], bevel=0.005, parent=shake)
    obj("WKnob", cyl_mesh("WK", 0.035, 0.03, 24), [chrome], loc=(0.18, -0.32, 0.79), rot=(math.pi / 2, 0, 0), parent=shake)
    box("WDisplay", 0.0, 0.12, -0.316, -0.31, 0.765, 0.815, [mat("lcd", hexlin("#1C2140"), 0.2)], parent=shake)
    lcd = mat("lcdtext", (0, 0, 0), 0.3, emit=hexlin("#7CF0C8"), estr=4.0)
    disp = {}
    for key in ("RUN", "END", "1:50"):
        disp[key] = text("WDisp_" + key, key, 0.03, [lcd], loc=(0.06, -0.318, 0.79), parent=shake, extrude=0.001)
    for fx in (-0.26, 0.26):
        for fy in (-0.26, 0.26):
            obj("WFoot", cyl_mesh("WF", 0.025, 0.03, 10), [mat("rubber", (0.05, 0.05, 0.05), 0.8)], loc=(fx, fy, 0.015), parent=shake)
    # drum: sits just in front of the body under a bulging porthole door, rotates about the y axis
    drum = empty("WDrum", loc=(0, -0.30, 0.42), parent=shake)
    obj("WDrumBack", cyl_mesh("WDB", 0.19, 0.01, 40), [mat("steel", (0.42, 0.44, 0.47), 0.35, metal=1.0)], loc=(0, -0.006, 0),
        rot=(math.pi / 2, 0, 0), parent=drum)
    for i in range(3):
        a = i * 2 * math.pi / 3
        box(f"WPaddle{i}", -0.015, 0.015, -0.03, -0.01, 0.12, 0.185, [mat("steel2", (0.7, 0.72, 0.75), 0.3, metal=1.0)], parent=drum).rotation_euler = (0, a, 0)
    drum_sets = {}
    for key, cols in (("N", A.NEIGHBOUR_LAUNDRY), ("J", A.JONAS_LAUNDRY)):
        s_ = empty("WDrumSet" + key, parent=drum, loc=(0, -0.05, 0))
        s_.scale = (1, 0.45, 1)
        for i, c in enumerate(cols + cols[:2]):
            a = i / (len(cols) + 2) * 2 * math.pi
            r_ = 0.11 if i < len(cols) else 0.03
            blob(f"WD{key}{i}", c, 0.075, s_, (r_ * math.cos(a), 0.0, r_ * math.sin(a) - 0.04), 77 + i)
        drum_sets[key] = s_
    obj("WGasket", torus_mesh("WGk", 0.19, 0.035, 40, 12), [mat("rubber2", hexlin("#3A3F4A"), 0.6)], loc=(0, -0.335, 0.42),
        rot=(math.pi / 2, 0, 0), parent=shake)
    # door on a hinge at the left edge: chrome ring + glass, bulging out in front of the body
    hinge = empty("WHinge", loc=(-0.2, -0.40, 0.42), parent=shake)
    obj("WRing", torus_mesh("WRing", 0.2, 0.032), [chrome], loc=(0.2, 0, 0), rot=(math.pi / 2, 0, 0), parent=hinge)
    obj("WGlass", sphere_mesh("WG", 0.19, 40, 20), [mat("glass", hexlin("#CFE0EC"), 0.03, alpha=0.18, coat=1.0)],
        loc=(0.2, 0.0, 0), scl=(1, 0.18, 1), parent=hinge)
    # sock hanging out of the door
    sock = obj("WSock", capsule_mesh("Sk", 0.032, 0.22), [cmat("pink")], loc=(0.04, -0.40, 0.27), rot=(0, 0.25, 0), parent=shake)
    # piles on top: neighbour's (moved out) and Jonas's (dumped)
    piles = {}
    for key, cols in (("N", A.NEIGHBOUR_LAUNDRY), ("J", A.JONAS_LAUNDRY)):
        p = empty("WPile" + key, loc=(0, 0, 0.86), parent=shake)
        for i, c in enumerate(cols + cols[:2]):
            blob(f"WP{key}{i}", c, 0.1, p, (R.uniform(-0.18, 0.18), R.uniform(-0.15, 0.15), 0.05 + (i // 3) * 0.06), 300 + i + (50 if key == "J" else 0))
        piles[key] = p
    note = empty("WNote", loc=(-0.04, -0.2, 1.25), parent=shake)
    obj("WNotePaper", box_mesh("NP", 0.56, 0.006, 0.36), [mat("paper", hexlin("#FFF6C8"), 0.8)], parent=note)
    obj("WNoteTape", box_mesh("NT", 0.12, 0.008, 0.035), [mat("tape", hexlin("#F2E6C8"), 0.4, alpha=1.0)], loc=(0, 0, 0.18), parent=note)
    text("WNoteText", "was in\nmy way!", 0.105, [mat("pen", hexlin("ink"), 0.6)], loc=(0, -0.005, 0.0), parent=note,
         extrude=0.0006)
    note.rotation_euler = (math.radians(-10), math.radians(-5), 0)
    return dict(root=root, shake=shake, drum=drum, drum_sets=drum_sets, hinge=hinge, sock=sock, piles=piles, note=note, disp=disp)


def torus_mesh(name, R_, r, seg=40, rs=12):
    bm = bmesh.new()
    ring = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        row = []
        for j in range(rs):
            b = 2 * math.pi * j / rs
            row.append(bm.verts.new(((R_ + r * math.cos(b)) * math.cos(a), (R_ + r * math.cos(b)) * math.sin(a), r * math.sin(b))))
        ring.append(row)
    for i in range(seg):
        for j in range(rs):
            bm.faces.new((ring[i][j], ring[(i + 1) % seg][j], ring[(i + 1) % seg][(j + 1) % rs], ring[i][(j + 1) % rs]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return me


# ------------------------------------------------------------------ characters
def person(name, look, with_face=True):
    skin = mat("skin_" + look["skin"], hexlin(look["skin"]), 0.55, sss=0.15)
    hood = cmat(look["hoodie"], 0.8, 0.5)
    pants = cmat(look["pants"], 0.85, 0.3)
    shoes = mat("shoe_" + look["shoes"], hexlin(look["shoes"]), 0.5, coat=0.3)
    hairm = mat("hair_" + look["hair"], hexlin(look["hair"]), 0.55, sheen=0.3)
    dark = mat("eyes", hexlin("#14151F"), 0.08, coat=1.0)
    white = mat("eyehl", (1, 1, 1), 0.2, emit=(1, 1, 1), estr=2)
    root = empty(name)
    hips = empty(name + "_hips", loc=(0, 0, 0.92), parent=root)
    obj(name + "_torso", box_mesh(name + "To", 0.46, 0.27, 0.6, 0.1, 3), [hood], loc=(0, 0, 0.27), parent=hips)
    obj(name + "_band", box_mesh(name + "Ba", 0.47, 0.28, 0.07, 0.03, 2), [hood], loc=(0, 0, 0.0), parent=hips)
    obj(name + "_pocket", box_mesh(name + "Pk", 0.26, 0.02, 0.13, 0.02, 2), [hood], loc=(0, -0.14, 0.12), parent=hips)
    obj(name + "_hood", torus_mesh(name + "Hd", 0.12, 0.05, 24, 10), [hood], loc=(0, 0.04, 0.6), rot=(0.25, 0, 0), parent=hips)
    for sx in (-0.04, 0.04):
        obj(name + "_str", cyl_mesh("Str", 0.006, 0.14, 6), [mat("string", (0.9, 0.9, 0.9), 0.6)], loc=(sx, -0.14, 0.48), parent=hips)
    obj(name + "_neck", cyl_mesh(name + "Nk", 0.055, 0.1, 16), [skin], loc=(0, 0, 0.62), parent=hips)
    head = empty(name + "_head", loc=(0, 0, 0.62), parent=hips)
    obj(name + "_skull", sphere_mesh(name + "Sk", 0.125, 32, 20), [skin], loc=(0, 0, 0.13), scl=(1.0, 0.96, 1.08), parent=head)
    parts = dict(root=root, hips=hips, head=head)
    if with_face:
        eyes = []
        for sx in (-0.045, 0.045):
            e = obj(name + "_eye", sphere_mesh("Ey", 0.019, 16, 12), [dark], loc=(sx, -0.112, 0.15), scl=(1, 0.6, 1.25), parent=head)
            obj(name + "_hl", sphere_mesh("Hl", 0.006, 8, 6), [white], loc=(0.006, -0.012, 0.007), parent=e)
            eyes.append(e)
        brows = []
        for sx in (-1, 1):
            b = empty(name + "_browp", loc=(sx * 0.047, -0.115, 0.195), parent=head)
            stroke(name + "_brow", [(-0.022, 0, 0), (0.022, 0, 0.004 * -sx * 0)], 0.007, [mat("brow", hexlin(look["hair"] if look["hair"] != "#8E8E8E" else "hair"), 0.6)], parent=b)
            brows.append(b)
        obj(name + "_nose", sphere_mesh("No", 0.018, 12, 8), [skin], loc=(0, -0.128, 0.12), parent=head)
        mouths = {}
        mpar = empty(name + "_mouth", loc=(0, -0.118, 0.075), parent=head)
        mouths["neutral"] = stroke(name + "_mN", [(-0.022, 0, 0), (0.022, 0, 0)], 0.006, [dark], parent=mpar)
        arc = lambda sgn: [(0.028 * math.cos(a), 0, sgn * 0.012 * (1 - math.sin(a)) - sgn * 0.006) for a in [math.pi * i / 10 for i in range(11)]]
        mouths["happy"] = stroke(name + "_mH", [(x, y, -z) for (x, y, z) in arc(1)], 0.006, [dark], parent=mpar)
        mouths["annoyed"] = stroke(name + "_mA", [(-0.02, 0, -0.004), (0.02, 0, 0.002)], 0.006, [dark], parent=mpar)
        mouths["tired"] = stroke(name + "_mT", [(-0.018, 0, -0.008), (0.018, 0, -0.008)], 0.005, [dark], parent=mpar)
        mouths["shock"] = obj(name + "_mO", sphere_mesh("MO", 0.018, 16, 10), [dark], scl=(0.9, 0.5, 1.3), loc=(0, 0.004, -0.004), parent=mpar)
        sweat = obj(name + "_sweat", sphere_mesh("Sw", 0.022, 12, 8), [mat("sweat", hexlin("#8FC1E3"), 0.05, coat=1.0)],
                    loc=(0.12, -0.06, 0.22), scl=(0.8, 0.8, 1.3), parent=head)
        parts.update(eyes=eyes, brows=brows, mouths=mouths, sweat=sweat)
    # hair
    st = look["style"]
    hr = random.Random(hash(name) % 9999)
    if st in ("short", "bun", "long", "cap", "curly"):
        obj(name + "_hcap", sphere_mesh("Hc", 0.133, 28, 16), [hairm], loc=(0, 0.012, 0.16), scl=(1.0, 1.0, 0.82), parent=head)
    if st == "bun":
        obj(name + "_bun", sphere_mesh("Bn", 0.07, 16, 12), [hairm], loc=(0, 0.06, 0.29), parent=head)
    if st == "long":
        obj(name + "_long", capsule_mesh("Lg", 0.1, 0.32), [hairm], loc=(0, 0.07, 0.2), scl=(1.2, 0.6, 1), parent=head)
    if st == "cap":
        capm = cmat("navy", 0.6, 0.2)
        obj(name + "_capd", sphere_mesh("Cd", 0.138, 28, 16), [capm], loc=(0, 0.01, 0.17), scl=(1, 1, 0.75), parent=head)
        obj(name + "_capb", cyl_mesh("Cb", 0.09, 0.015, 24), [capm], loc=(0, -0.13, 0.205), scl=(1.1, 1.0, 1), parent=head)
    if st == "curly":
        for i in range(46):
            th = hr.uniform(0, 2 * math.pi)
            ph = hr.uniform(0, math.radians(78))
            if math.sin(th) < -0.55 and ph > math.radians(45):      # keep the forehead/face free
                continue
            r = 0.135
            p = (r * math.sin(ph) * math.cos(th), r * math.sin(ph) * math.sin(th) * 0.96 + 0.008, 0.13 + r * math.cos(ph) * 1.05)
            s = hr.uniform(0.036, 0.048)
            obj(name + "_curl", ico_mesh("Cu", 1, 3), [hairm], loc=p, scl=(s, s, s), parent=head)
    # arms (pivot at shoulder) and legs (pivot at hip)
    arms, legs = [], []
    for sx in (-1, 1):
        sh = empty(name + "_shoulder", loc=(sx * 0.27, 0, 0.5), parent=hips)
        obj(name + "_arm", capsule_mesh(name + "Ar", 0.07, 0.56), [hood], parent=sh)
        obj(name + "_hand", sphere_mesh("Hn", 0.055, 16, 10), [skin], loc=(0, 0, -0.6), parent=sh)
        arms.append(sh)
        hp = empty(name + "_hip", loc=(sx * 0.11, 0, -0.02), parent=hips)
        obj(name + "_leg", capsule_mesh(name + "Lg", 0.085, 0.8), [pants], parent=hp)
        obj(name + "_shoe", box_mesh(name + "Sh", 0.13, 0.27, 0.1, 0.04, 3), [shoes], loc=(0, -0.05, -0.85), parent=hp)
        legs.append(hp)
    parts.update(arms=arms, legs=legs)
    bk, heap = basket(name + "_basket", hips, ["white"], loc=(0, -0.34, -0.12))
    parts.update(basket=bk, heap_default=heap)
    return parts


def set_basket_colors(parts, colors):
    """replace the default heap with the given colours (keeps one heap object for full/empty switching)"""
    heap = parts["heap_default"]
    for c in list(heap.children):
        bpy.data.objects.remove(c, do_unlink=True)
    for i, col in enumerate(colors):
        blob(f"{heap.name}_c{i}", col, 0.1, heap, ((i % 3 - 1) * 0.14, (i // 3 - 0.5) * 0.12, 0.2 + (i % 2) * 0.04), hash(heap.name) % 1000 + i)


# ------------------------------------------------------------------ poses
def walk_angles(walked, moving, stride=1.25):
    if not moving:
        return 0.0, 0.0, 0.0
    ph = walked / stride * 2 * math.pi
    return 0.5 * math.sin(ph), -0.5 * math.sin(ph), 0.035 * abs(math.sin(ph))


def heading_for(face_dir, toward_cam=0.0):
    """face_dir +1 = moving/looking right (+x), -1 = left; toward_cam turns the face towards the camera"""
    return face_dir * (math.pi / 2 - toward_cam)


def pose_frame(t, who):
    """per-frame pose for Jonas ('J') or neighbour index i"""
    if who == "J":
        if A.is_close(t):
            c = A.jonas_close(t)
            moving = c["walk"] is not None
            walked = c["walk"] or 0.0
            lA, lB, bob = walk_angles(walked, moving, 1.1)
            ang = heading_for(c["face"], 0.0 if moving else 0.85)
            arm = -0.5 if c["basket"] is not None else 0.0
            arms = (arm, arm)
            lean = 0.0
            if c["pose"] == "reach":
                k = c["pose_k"]
                arms = (-1.1 - 0.5 * k, -1.1 - 0.5 * k)
                lean = 0.18 + 0.12 * k
                ang = heading_for(1, 0.25)
            if c["basket"] is None and c["pose"] != "reach":
                arms = (-0.35 * lB, -0.35 * lA) if moving else (0.05, 0.05)
            tapA = 0.12 * max(0.0, math.sin(c["tap"])) if c["tap"] else 0.0
            return dict(loc=(c["x"], 2.0, 0.0), rot=ang, legs=(lA, lB + tapA), arms=arms, bob=bob, lean=lean,
                        expr=c["expr"], sweat=c["sweat"], basket=c["basket"], floor_basket=c["floor_basket"],
                        holding=c["holding"], visible=True, scale=1.0, headtilt=0.12 if c["expr"] == "tired" else 0.0)
        j = A.jonas_overview(t)
        pos, face, walked, _ = A.along(0, "L", j["u"])
        d = -face if j["rev"] else face
        moving = j["moving"]
        lA, lB, bob = walk_angles(walked, moving)
        ang = heading_for(d) if moving else heading_for(j["face"] or 1, 0.7)
        arm = -0.5 if j["basket"] is not None else 0.0
        return dict(loc=pos, rot=ang, legs=(lA, lB), arms=(arm, arm), bob=bob, lean=0.0, expr="neutral", sweat=0.0,
                    basket=j["basket"], floor_basket=None, holding=None, visible=j["visible"], scale=1.0, headtilt=0.0)
    n = A.neighbour(t, who)
    look, lv, side, off, spd, bcol = A.NEIGHBOURS[who]
    pos, face, walked, _ = A.along(lv, side, n["u"])
    d = -face if n["rev"] else face
    lA, lB, bob = walk_angles(walked + who * 0.37, True)
    k = A.crowd_k(t)
    return dict(loc=pos, rot=heading_for(d), legs=(lA, lB), arms=(-0.5, -0.5), bob=bob, lean=0.0, expr="neutral", sweat=0.0,
                basket=bcol, floor_basket=None, holding=None, visible=k > 0.001, scale=max(1e-4, k), headtilt=0.0)


EXPR = {  # eye scale z, eye scale x, brow z offset, brow rotation (inner down = +), mouth
    "neutral": (1.0, 1.0, 0.0, 0.0, "neutral"),
    "shock": (1.4, 1.2, 0.018, -0.15, "shock"),
    "tired": (0.42, 1.0, -0.008, -0.25, "tired"),
    "annoyed": (0.7, 1.0, -0.01, 0.38, "annoyed"),
    "happy": (0.55, 1.05, 0.012, -0.1, "happy"),
}


# ------------------------------------------------------------------ camera
def camera_frame(t):
    """-> pos, target, lens, focus point, f-stop"""
    wide_t = (0.0, 1.6, 3.6)
    el, az, dist, lens = math.radians(5.5), math.radians(-7.0), 62.0, 60.0
    wide_c = (wide_t[0] + dist * math.cos(el) * math.sin(az), wide_t[1] - dist * math.cos(el) * math.cos(az), wide_t[2] + dist * math.sin(el))
    if A.is_close(t):
        c = A.jonas_close(t)
        s = c["settle"]
        wx = A.WASHER[0]
        tgt = (wx - 0.67, 2.25, 0.55)
        pos = (wx - 0.45, -2.3 - 0.5 * s, 1.25 + 0.1 * s)
        foc = (c["x"], 2.0, 1.2)
        if A.ins(t, T["s8"]):
            k = 0.18 * A.tw(t, T["note8"] + 0.1, 1.6, A.ease_in_out)
            P = (wx - 0.62, 2.1, 0.95)
            tgt = tuple(tgt[i] + (P[i] - tgt[i]) * k * 2.0 for i in range(3))
            pos = tuple(pos[i] + (P[i] - pos[i]) * k for i in range(3))
            foc = (wx - 0.6, 2.0, 1.3)
        return pos, tgt, 32.0, foc, 3.2
    z = A.zoom_at(t)
    P = (A.WASHER[0] - 0.2, 2.3, 0.75)
    pos = tuple(P[i] + (wide_c[i] - P[i]) / z for i in range(3))
    tgt = tuple(P[i] + (wide_t[i] - P[i]) / z for i in range(3))
    return pos, tgt, lens, tgt, 11.0


def look_quat(cam, tgt):
    d = Vector(tgt) - Vector(cam)
    return d.to_track_quat("-Z", "Y")


# ------------------------------------------------------------------ build + bake
def build():
    global COL
    clear_scene()
    _M.clear()
    COL = bpy.context.scene.collection
    setup_render()
    build_house()
    mh, hh = build_clock()
    W = build_washer()
    # sun through the open front + soft fill
    sun = bpy.data.lights.new("Sun", "SUN"); sun.energy = 3.2; sun.angle = math.radians(4); sun.color = (1.0, 0.94, 0.85)
    obj("SunO", sun, rot=(math.radians(52), math.radians(-18), math.radians(-28)))
    fill = bpy.data.lights.new("CloseFill", "AREA"); fill.shape = "DISK"; fill.size = 2.5; fill.energy = 150; fill.color = (1.0, 0.92, 0.84)
    obj("CloseFillO", fill, loc=(A.WASHER[0] - 1.6, -1.2, 2.3), rot=(math.radians(60), 0, math.radians(-15)))
    J = person("Jonas", A.JONAS)
    set_basket_colors(J, A.JONAS_LAUNDRY)
    # Jonas's basket on the floor (s6) and a held cloth
    fb, fheap = basket("FloorBasket", None, A.JONAS_LAUNDRY, loc=(A.WASHER[0] - (700 - 196) * A.PX_M, 2.15, 0.0))
    hold = {c: blob("Hold_" + c, c, 0.075, J["arms"][1], (0, -0.05, -0.66), 900 + i) for i, c in enumerate(("pink", "gold"))}
    NB = []
    for i, (look, lv, side, off, spd, bcol) in enumerate(A.NEIGHBOURS):
        p = person(f"NB{i}", look, with_face=False)
        set_basket_colors(p, bcol)
        NB.append(p)
    cd = bpy.data.cameras.new("Cam"); cd.sensor_fit = "AUTO"; cd.sensor_width = 36.0
    cd.clip_start, cd.clip_end = 0.05, 400.0
    cd.dof.use_dof = True; cd.dof.aperture_blades = 7
    cam = obj("Cam", cd); cam.rotation_mode = "QUATERNION"
    bpy.context.scene.camera = cam
    return dict(J=J, NB=NB, W=W, cam=cam, mh=mh, hh=hh, fb=fb, fheap=fheap, hold=hold)


def bake(S):
    frames = list(range(N))
    ts = [f / FPS for f in frames]
    cuts = sorted({int(round(T[s][0] * FPS)) for s in ("s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9")})

    def step_cuts(o, path, n):
        for i in range(n):
            fc = fcurve_of(o, path, i)
            if fc is None:
                continue
            for kp in fc.keyframe_points:
                if int(round(kp.co[0])) + 1 in cuts:
                    kp.interpolation = "CONSTANT"

    # characters
    for who, P in [("J", S["J"])] + [(i, p) for i, p in enumerate(S["NB"])]:
        poses = [pose_frame(t, who) for t in ts]
        root, hips = P["root"], P["hips"]
        for i in range(3):
            keys(root, "location", i, frames, [p["loc"][i] for p in poses])
        keys(root, "rotation_euler", 2, frames, unwrap([p["rot"] for p in poses]))
        sc = [p["scale"] if p["visible"] else 1e-4 for p in poses]
        for i in range(3):
            keys(root, "scale", i, frames, sc)
        keys(hips, "location", 2, frames, [0.92 + p["bob"] for p in poses])
        keys(hips, "rotation_euler", 0, frames, [p["lean"] for p in poses])
        for k in range(2):
            keys(P["legs"][k], "rotation_euler", 0, frames, [p["legs"][k] for p in poses])
            keys(P["arms"][k], "rotation_euler", 0, frames, [p["arms"][k] for p in poses])
        keys(P["head"], "rotation_euler", 0, frames, [p["headtilt"] for p in poses])
        vis_keys(P["basket"], frames, [p["basket"] is not None for p in poses])
        vis_keys(P["heap_default"], frames, [bool(p["basket"]) for p in poses])
        step_cuts(root, "location", 3); step_cuts(root, "rotation_euler", 3)
        if who == "J":
            blinks = [3.2, 6.0, 9.2, 13.6, 16.6, 20.4, 23.8]
            ez, ex, bz, br, mo = zip(*[EXPR[p["expr"]] for p in poses])
            ez = [0.08 if any(b <= t < b + 0.1 for b in blinks) else v for t, v in zip(ts, ez)]
            for e in P["eyes"]:
                keys(e, "scale", 2, frames, [1.25 * v for v in ez])
                keys(e, "scale", 0, frames, [1.0 * v for v in ex])
            for side, b in zip((-1, 1), P["brows"]):
                keys(b, "location", 2, frames, [0.195 + v for v in bz])
                keys(b, "rotation_euler", 1, frames, [side * v for v in br])
            for name, m in P["mouths"].items():
                vis_keys(m, frames, [v == name for v in mo])
            s = [max(1e-4, p["sweat"]) for p in poses]
            for i in range(3):
                keys(P["sweat"], "scale", i, frames, [v * (0.8, 0.8, 1.3)[i] for v in s])
            vis_keys(S["fb"], frames, [p["floor_basket"] is not None for p in poses])
            vis_keys(S["fheap"], frames, [bool(p["floor_basket"]) for p in poses])
            for c, o in S["hold"].items():
                vis_keys(o, frames, [p["holding"] == c for p in poses])
    # washer
    W = S["W"]
    st = [A.washer_state(t) for t in ts]
    rot, a = [], 0.0
    for t, s in zip(ts, st):
        a += (7.0 if s["state"] == "running" else 0.0) / FPS
        rot.append(a)
    keys(W["drum"], "rotation_euler", 1, frames, rot)
    keys(W["shake"], "rotation_euler", 1, frames, [0.012 * math.sin(t * 47) if s["state"] == "running" else 0.0 for t, s in zip(ts, st)])
    keys(W["shake"], "location", 0, frames, [0.004 * math.sin(t * 61) if s["state"] == "running" else 0.0 for t, s in zip(ts, st)])
    keys(W["hinge"], "rotation_euler", 2, frames, [-1.9 * s["door"] for s in st])
    vis_keys(W["drum_sets"]["N"], frames, [s["drum"] == A.NEIGHBOUR_LAUNDRY for s in st])
    vis_keys(W["drum_sets"]["J"], frames, [s["drum"] == A.JONAS_LAUNDRY for s in st])
    vis_keys(W["sock"], frames, [s["sock"] for s in st])
    for key, cols in (("N", A.NEIGHBOUR_LAUNDRY), ("J", A.JONAS_LAUNDRY)):
        o = W["piles"][key]
        v = [max(1e-4, s["pileK"]) if s["pile"] == cols else 1e-4 for s in st]
        for i in range(3):
            keys(o, "scale", i, frames, v)
    for key, o in W["disp"].items():
        vis_keys(o, frames, [s["display"] == key for s in st])
    nk = [max(1e-4, A.note_k(t)) for t in ts]
    for i in range(3):
        keys(W["note"], "scale", i, frames, nk)
    # clock
    keys(S["mh"], "rotation_euler", 1, frames, [math.radians(A.clock_minutes(t) * 6) for t in ts])
    # camera
    cam = S["cam"]
    cs = [camera_frame(t) for t in ts]
    qs, prev = [], None
    for (pos, tgt, lens, foc, fst) in cs:
        q = look_quat(pos, tgt)
        if prev is not None and q.dot(prev) < 0:
            q.negate()
        qs.append(q); prev = q
    for i in range(3):
        keys(cam, "location", i, frames, [c[0][i] for c in cs])
    for i in range(4):
        keys(cam, "rotation_quaternion", i, frames, [q[i] for q in qs])
    keys(cam.data, "lens", None, frames, [c[2] for c in cs])
    fd = []
    for (pos, tgt, lens, foc, fst) in cs:
        fw = (Vector(tgt) - Vector(pos)).normalized()
        fd.append(max(0.1, (Vector(foc) - Vector(pos)).dot(fw)))
    keys(cam.data, "dof.focus_distance", None, frames, fd)
    keys(cam.data, "dof.aperture_fstop", None, frames, [c[4] for c in cs])
    step_cuts(cam, "location", 3); step_cuts(cam, "rotation_quaternion", 4)
    bpy.context.scene.frame_set(0)


def export_proj(S):
    """screen positions (px) of Jonas's head and the washer, for the JONAS / WASHER labels in s1"""
    from bpy_extras.object_utils import world_to_camera_view
    sc = bpy.context.scene
    out = {}
    for f in range(0, int(2.4 * FPS)):
        sc.frame_set(f)
        dg = bpy.context.evaluated_depsgraph_get()
        cam = S["cam"].evaluated_get(dg)
        jh = S["J"]["head"].matrix_world.translation + Vector((0, 0, 0.55))
        wt = Vector((A.WASHER[0], A.WASHER[1] - 0.3, 1.05))
        res = {}
        for k, p in (("jonas", jh), ("washer", wt)):
            v = world_to_camera_view(sc, cam, p)
            res[k] = (round(v.x * 1080, 1), round((1 - v.y) * 1920, 1))
        out[f] = res
    json.dump(out, open(os.path.join(BASE, "proj028.json"), "w"))
    sc.frame_set(0)


def run(save=True):
    S = build()
    bake(S)
    export_proj(S)
    if save:
        os.makedirs(os.path.join(BASE, "frames"), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE, "biz1_blender.blend"))
    print("built 028:", N, "frames,", len(bpy.data.objects), "objects")


if globals().get("RUN", True):
    run(globals().get("SAVE", True))
