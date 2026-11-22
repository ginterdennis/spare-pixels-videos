"""027 "The pixel that fell out": builds the whole Blender scene and bakes every frame.

Run inside Blender (5.3, EEVEE) with BASE pointing at a folder that holds anim.py and art.json:
    BASE = "~/Movies/spare-pixels-blender/027"; exec(open(BASE + "/build.py").read())
Everything that moves comes from anim.py (pure Python, testable outside Blender).
"""
import bpy, bmesh, math, json, os, types, random
from mathutils import Vector, Matrix

BASE = os.path.expanduser(globals().get("BASE", "~/Movies/spare-pixels-blender/027"))


def _load(name):
    path = os.path.join(BASE, name)
    if os.path.exists(path):
        return open(path).read()
    return bpy.data.texts[name].as_string()


anim = types.ModuleType("anim")
exec(_load("anim.py"), anim.__dict__)
ART = json.loads(_load("art.json"))
A = anim
EV = A.build()
FPS, N = A.FPS, A.N


# ------------------------------------------------------------------ utilities
def lin(c):
    """sRGB 0-255 -> linear 0-1"""
    out = []
    for v in c[:3]:
        v = v / 255
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


def mat(name, base=(0.5, 0.5, 0.5), rough=0.5, coat=0.0, emit=None, estr=0.0, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*base, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Coat Roughness"].default_value = 0.06
    if emit is not None:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = estr
    return m


def obj(name, me, mats=(), loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    for m_ in mats:
        o.data.materials.append(m_)
    o.location, o.rotation_euler = loc, rot
    if parent:
        o.parent = parent
    return o


def box_mesh(name, sx, sy, sz, bevel=0.0, seg=3, center=(0, 0, 0)):
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


def cyl_mesh(name, r, h, verts=48, cap_top=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts, radius1=r, radius2=r, depth=h)
    bmesh.ops.translate(bm, vec=(0, 0, h / 2), verts=bm.verts)
    if not cap_top:
        top = [f for f in bm.faces if f.normal.z > 0.9]
        bmesh.ops.delete(bm, geom=top, context="FACES_ONLY")
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    return me


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
    cb = anim_utils.action_get_channelbag_for_slot(act, ad.action_slot)
    return cb.fcurves.find(path, index=index)


def keys(idd, path, index, frames, values, interp="LINEAR"):
    """write a whole curve at once (fast). values[i] at frames[i]."""
    if not frames:
        return
    prop = idd.path_resolve(path)
    try:
        prop[index] = values[0]
    except TypeError:
        setattr(idd, path, values[0])
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


def changes(frames, values, eps=1e-7):
    """keep only the frames where a constant-interpolated value changes"""
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


# ------------------------------------------------------------------ scene
def setup_render():
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 0, N - 1
    sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1080, 1920, 100
    ee = sc.eevee
    for k, v in dict(taa_render_samples=32, taa_samples=16, use_raytracing=True, bokeh_max_size=180.0,
                     use_shadows=True, shadow_ray_count=2, shadow_step_count=8,
                     use_fast_gi=True).items():
        try:
            setattr(ee, k, v)
        except Exception as e:
            print("eevee setting skipped:", k, e)
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = 0.5
    try:
        sc.render.motion_blur_position = "START"     # no smear across hard cuts
    except Exception as e:
        print("motion_blur_position skipped:", e)
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = "JPEG"
    sc.render.image_settings.quality = 95
    sc.render.filepath = os.path.join(BASE, "frames", "f_")
    w = sc.world or bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (0.0045, 0.005, 0.014, 1)
    bg.inputs[1].default_value = 1.0


def build_set():
    sc = bpy.context.scene
    # materials
    M = {}
    tile = bpy.data.materials.new("M_Tile")
    tile.use_nodes = True
    nt = tile.node_tree
    b = nt.nodes["Principled BSDF"]
    oi = nt.nodes.new("ShaderNodeObjectInfo")
    mul = nt.nodes.new("ShaderNodeMixRGB"); mul.blend_type = "MULTIPLY"; mul.inputs[0].default_value = 1.0
    mul.inputs[2].default_value = (0.30, 0.30, 0.30, 1)
    nt.links.new(oi.outputs["Color"], mul.inputs[1])
    nt.links.new(mul.outputs[0], b.inputs["Base Color"])
    nt.links.new(oi.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 0.80
    b.inputs["Roughness"].default_value = 0.30
    b.inputs["Coat Weight"].default_value = 0.6
    b.inputs["Coat Roughness"].default_value = 0.05
    M["tile"] = tile
    M["bezel"] = mat("M_Bezel", (0.014, 0.017, 0.048), 0.30, coat=0.5)
    M["recess"] = mat("M_Recess", (0.002, 0.002, 0.004), 0.85)
    M["foot"] = mat("M_Foot", (0.010, 0.012, 0.032), 0.35, coat=0.3)
    M["eye"] = mat("M_Eye", (0.002, 0.002, 0.003), 0.08, coat=1.0)
    M["spark"] = mat("M_Spark", (1, 1, 1), 0.2, emit=(1, 1, 1), estr=3.0)
    M["pad"] = mat("M_Pad", lin((255, 110, 185)), 0.85)
    M["padside"] = mat("M_PadSide", lin((235, 90, 165)), 0.9)
    M["bookA"] = mat("M_BookA", lin((40, 140, 210)), 0.45, coat=0.2)
    M["bookB"] = mat("M_BookB", lin((200, 50, 120)), 0.45, coat=0.2)
    M["pages"] = mat("M_Pages", lin((236, 228, 205)), 0.9)
    M["mug"] = mat("M_Mug", lin((90, 200, 255)), 0.12, coat=0.8)
    M["mugin"] = mat("M_MugIn", lin((240, 242, 250)), 0.15)
    M["coffee"] = mat("M_Coffee", lin((40, 20, 10)), 0.04, coat=1.0)
    M["pencil"] = mat("M_Pencil", lin((255, 205, 90)), 0.35, coat=0.4)
    M["eraser"] = mat("M_Eraser", lin((255, 120, 170)), 0.8)
    M["wood"] = mat("M_Wood", (0.2, 0.1, 0.05), 0.45)
    M["graphite"] = mat("M_Graphite", (0.02, 0.02, 0.025), 0.3, metal=0.5)
    # wood desk: wave bands warped by noise
    wd = M["wood"]; nt = wd.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.0, 7.0, 1.0)
    wv = nt.nodes.new("ShaderNodeTexWave"); wv.wave_type = "BANDS"; wv.bands_direction = "Y"
    wv.inputs["Scale"].default_value = 26.0; wv.inputs["Distortion"].default_value = 9.0
    wv.inputs["Detail"].default_value = 3.0; wv.inputs["Detail Scale"].default_value = 1.2
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 90.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (*lin((52, 28, 16)), 1)
    ramp.color_ramp.elements[1].color = (*lin((112, 66, 36)), 1)
    mix = nt.nodes.new("ShaderNodeMath"); mix.operation = "MULTIPLY_ADD"
    mix.inputs[1].default_value = 0.75
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs[0], wv.inputs["Vector"])
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    nt.links.new(wv.outputs["Fac"], mix.inputs[0])
    nt.links.new(nz.outputs["Fac"], mix.inputs[2])
    nt.links.new(mix.outputs[0], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], b.inputs["Base Color"])
    # bokeh city lights
    bok = []
    for k, c in enumerate([(255, 196, 120), (255, 120, 190), (110, 200, 255), (255, 215, 110), (190, 160, 255)]):
        bok.append(mat(f"M_Bokeh{k}", (0, 0, 0), 1.0, emit=lin(c), estr=9.0))

    # desk
    me = bpy.data.meshes.new("Desk")
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=2.0)
    bm.to_mesh(me); bm.free()
    obj("Desk", me, [M["wood"]], loc=(0, 0.9, 0))

    # monitor housing: a box with the front face inset and pushed in (the recess the tiles sit in)
    sx0, sx1, sz0, sz1 = -0.25, 0.25, 0.035, 0.685
    yf, yb, yr = A.BEZEL_FRONT, 0.10, 0.014
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(sx1 - sx0, yb - yf, sz1 - sz0), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(0, (yb + yf) / 2, (sz0 + sz1) / 2), verts=bm.verts)
    bm.faces.ensure_lookup_table()
    front = [f for f in bm.faces if f.normal.y < -0.9][0]
    bmesh.ops.inset_region(bm, faces=[front], thickness=0.025, depth=0.0, use_even_offset=True)
    for v in front.verts:
        v.co.y = yr
    front.material_index = 1
    bmesh.ops.bevel(bm, geom=[e for e in bm.edges if not all(abs(v.co.y - yr) < 1e-6 for v in e.verts)],
                    offset=0.0035, segments=3, profile=0.5, affect="EDGES")
    me = bpy.data.meshes.new("Housing"); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    obj("Housing", me, [M["bezel"], M["recess"]])
    obj("Foot", box_mesh("Foot", 0.30, 0.115, 0.035, bevel=0.004, center=(0, 0.0525, 0.0175)), [M["foot"]])
    led = obj("LED", box_mesh("LED", 0.010, 0.002, 0.003, bevel=0.0008), [M["spark"]],
              loc=(0.205, yf - 0.0005, 0.047))
    led.active_material = mat("M_LED", (0, 0, 0), 0.3, emit=lin((255, 211, 107)), estr=4.0)

    # tiles
    tmesh = box_mesh("Tile", A.S, A.S, A.S, bevel=0.0024, seg=3)
    paw = bpy.data.objects.new("Paw", None)
    sc.collection.objects.link(paw)
    paw.location = A.PAW_C
    paw.empty_display_size = 0.03
    tiles = {}
    look = ART["states"]["look_c"]
    for r in range(A.ROWS):
        for c in range(A.COLS):
            if (r, c) == tuple(A.HOLE_RC):
                continue
            o = obj(f"T_{r:02d}_{c:02d}", tmesh, [], loc=A.tile_xyz(r, c))
            o.color = (*lin(look[r][c]), 1)
            if (r, c) in [tuple(x) for x in A.PAW_RC]:
                o.parent = paw
                o.location = ((c - 5) * A.P, 0.0, (21 - r) * A.P)
            tiles[(r, c)] = o
    tmesh.materials.append(M["tile"])

    # the hero: a tile with eyes
    hmesh = box_mesh("HeroMesh", A.S, A.S, A.S, bevel=0.0024, seg=3)
    hmesh.materials.append(M["tile"])
    hero = obj("Hero", hmesh, [], loc=(A.H0[0], A.H0[1], A.HALF))
    hero.color = (*lin((255, 211, 107)), 1)
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=1.0)
    eme = bpy.data.meshes.new("EyeMesh"); bm.to_mesh(eme); bm.free()
    for p in eme.polygons:
        p.use_smooth = True
    eme.materials.append(M["eye"])
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=1.0)
    sme = bpy.data.meshes.new("SparkMesh"); bm.to_mesh(sme); bm.free()
    sme.materials.append(M["spark"])
    for side, sgn in (("L", -1), ("R", 1)):
        e = obj("Eye" + side, eme, [], parent=hero)
        e.location = (sgn * 0.0042, -A.HALF - 0.0002, 0.0016)
        e.scale = (0.0019, 0.0007, 0.0029)
        s = obj("Spark" + side, sme, [], parent=e)
        s.location = (-0.35, -0.9, 0.45)
        s.scale = (0.28, 0.28, 0.20)
    glow = bpy.data.lights.new("HeroGlow", "POINT")
    glow.color = lin((255, 211, 107)); glow.energy = 0.12; glow.shadow_soft_size = 0.008
    obj("HeroGlow", glow, [])

    # props
    px, py = A.PAD["c"]
    obj("Pad", box_mesh("Pad", 0.076, 0.076, A.PAD["h"], bevel=0.0012, center=(0, 0, A.PAD["h"] / 2)),
        [M["pad"]], loc=(px, py, 0), rot=(0, 0, math.radians(-12)))
    bx, by = A.BOOKS["c"]
    for k, (w_, d_, h_, z_, rz, cov) in enumerate([(0.15, 0.21, 0.025, 0.0, 8, "bookA"),
                                                     (0.14, 0.20, 0.022, 0.025, -5, "bookB")]):
        root = bpy.data.objects.new(f"Book{k}", None); sc.collection.objects.link(root)
        root.location = (bx, by, z_); root.rotation_euler = (0, 0, math.radians(rz))
        cv = 0.0025
        obj(f"Book{k}_bot", box_mesh(f"B{k}b", w_, d_, cv, 0.0008, center=(0, 0, cv / 2)), [M[cov]], parent=root)
        obj(f"Book{k}_top", box_mesh(f"B{k}t", w_, d_, cv, 0.0008, center=(0, 0, h_ - cv / 2)), [M[cov]], parent=root)
        obj(f"Book{k}_sp", box_mesh(f"B{k}s", cv, d_, h_, 0.0008, center=(-w_ / 2 + cv / 2, 0, h_ / 2)), [M[cov]],
            parent=root)
        obj(f"Book{k}_pg", box_mesh(f"B{k}p", w_ - 0.008, d_ - 0.008, h_ - 2 * cv, 0.0005,
                                     center=(0.001, 0, h_ / 2)), [M["pages"]], parent=root)
    # mug: open cylinder + solidify, coffee disc, handle
    mx, my = A.MUG["c"]
    mm = cyl_mesh("Mug", A.MUG["r"], A.MUG["h"], 64, cap_top=False)
    mug = obj("Mug", mm, [M["mug"], M["mugin"]], loc=(mx, my, 0))
    sol = mug.modifiers.new("Solid", "SOLIDIFY"); sol.thickness = 0.004; sol.offset = -1
    sol.material_offset = 1
    bev = mug.modifiers.new("Bevel", "BEVEL"); bev.width = 0.0015; bev.segments = 3
    obj("Coffee", cyl_mesh("Coffee", A.MUG["r"] - 0.004, 0.001, 64), [M["coffee"]], loc=(mx, my, 0.080))
    tor = bpy.data.meshes.new("Handle")
    bm = bmesh.new()
    R, rr = 0.016, 0.0055
    ring = []
    for i in range(40):
        a = 2 * math.pi * i / 40
        row = []
        for j in range(16):
            b_ = 2 * math.pi * j / 16
            x = (R + rr * math.cos(b_)) * math.cos(a)
            z = (R + rr * math.cos(b_)) * math.sin(a)
            y = rr * math.sin(b_)
            row.append(bm.verts.new((x, y, z)))
        ring.append(row)
    for i in range(40):
        for j in range(16):
            bm.faces.new((ring[i][j], ring[(i + 1) % 40][j], ring[(i + 1) % 40][(j + 1) % 16], ring[i][(j + 1) % 16]))
    bm.to_mesh(tor); bm.free()
    for p in tor.polygons:
        p.use_smooth = True
    obj("Handle", tor, [M["mug"]], loc=(mx, my + A.MUG["r"] + 0.009, 0.052), rot=(0, 0, math.radians(90)))
    # pencil
    pen = bpy.data.objects.new("Pencil", None); sc.collection.objects.link(pen)
    pen.location = (0.16, -0.21, 0.0045); pen.rotation_euler = (0, math.radians(90), math.radians(-22))
    obj("PencilBody", cyl_mesh("PB", 0.0045, 0.15, 6), [M["pencil"]], parent=pen)
    obj("PencilEraser", cyl_mesh("PE", 0.0042, 0.012, 24), [M["eraser"]], loc=(0, 0, -0.012), parent=pen)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=0.0045, radius2=0.0006, depth=0.022)
    bmesh.ops.translate(bm, vec=(0, 0, 0.011), verts=bm.verts)
    tip = bpy.data.meshes.new("PT"); bm.to_mesh(tip); bm.free()
    obj("PencilTip", tip, [mat("M_PencilWood", lin((222, 180, 130)), 0.7)], loc=(0, 0, 0.15), parent=pen)

    # bokeh lights far behind the monitor
    rnd = random.Random(27)
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=2, radius=1.0)
    bme = bpy.data.meshes.new("BokehMesh"); bm.to_mesh(bme); bm.free()
    for k in range(46):
        o = obj(f"Bokeh{k}", bme, [], loc=(rnd.uniform(-1.4, 1.4), rnd.uniform(1.6, 3.4), rnd.uniform(0.12, 1.5)))
        s = rnd.uniform(0.010, 0.026); o.scale = (s, s, s)
        o.active_material = bok[k % len(bok)]

    # lights
    def light(name, kind, loc, aim, energy, color, size=0.1, size_y=None, spot=None):
        L = bpy.data.lights.new(name, kind)
        L.energy, L.color = energy, color
        if kind == "AREA":
            L.shape = "RECTANGLE"; L.size = size; L.size_y = size_y or size
        else:
            L.shadow_soft_size = size
        if spot:
            L.spot_size, L.spot_blend = math.radians(spot), 0.55
        o = obj(name, L, [], loc=loc)
        d = Vector(aim) - Vector(loc)
        o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        return o
    light("ScreenGlow", "AREA", (0, -0.045, 0.36), (0, -1.0, 0.36), 5.0, (0.62, 0.66, 1.0), 0.44, 0.58)
    light("Lamp", "SPOT", (-0.55, -0.55, 0.62), (-0.12, -0.12, 0.0), 22.0, (1.0, 0.74, 0.48), 0.06, spot=60)
    light("Rim", "AREA", (0.45, 0.25, 0.22), (-0.12, -0.10, 0.04), 5.0, (0.45, 0.75, 1.0), 0.30)
    light("Fill", "AREA", (0.0, -1.2, 0.35), (0.0, 0.0, 0.25), 2.0, (0.70, 0.72, 1.0), 0.8)

    # camera
    cd = bpy.data.cameras.new("Cam")
    cd.sensor_fit = "AUTO"; cd.sensor_width = 36.0
    cd.clip_start, cd.clip_end = 0.005, 20.0
    cd.dof.use_dof = True; cd.dof.aperture_blades = 7; cd.dof.aperture_rotation = math.radians(12)
    cam = obj("Cam", cd, [])
    cam.rotation_mode = "QUATERNION"
    sc.camera = cam
    return tiles, paw


# ------------------------------------------------------------------ animation bake
LOOK_GAIN = 0.0011


def bake(tiles, paw):
    sc = bpy.context.scene
    frames = list(range(N))
    ts = [f / FPS for f in frames]
    # hero
    hero = bpy.data.objects["Hero"]
    hero.rotation_mode = "XYZ"
    poses = [A.hero(t) for t in ts]
    for i in range(3):
        keys(hero, "location", i, frames, [p.loc[i] for p in poses])
        keys(hero, "scale", i, frames, [p.scl[i] for p in poses])
        keys(hero, "rotation_euler", i, frames, unwrap([p.rot[i] for p in poses]))
    eL, eR = bpy.data.objects["EyeL"], bpy.data.objects["EyeR"]
    wink = EV["wink"]
    for e, sgn in ((eL, -1), (eR, 1)):
        lx, lz, sx, sz = [], [], [], []
        for t, p in zip(ts, poses):
            lid = p.lid
            for b_ in A.blinks():
                if b_ <= t < b_ + 0.12:
                    lid = min(lid, 0.08)
            if sgn < 0 and wink <= t < wink + 0.18:
                lid = 0.08
            lx.append(sgn * 0.0042 + p.look[0] * LOOK_GAIN)
            lz.append(0.0016 + p.look[1] * LOOK_GAIN)
            sx.append(0.0019 * p.eye)
            sz.append(max(0.00005, 0.0029 * p.eye * lid))
        keys(e, "location", 0, frames, lx)
        keys(e, "location", 2, frames, lz)
        keys(e, "scale", 0, frames, sx)
        keys(e, "scale", 2, frames, sz)
        keys(e, "scale", 1, frames, [0.0007 * min(1, p.eye) if p.eye > 0.01 else 0.00005 for p in poses])
    gl = bpy.data.objects["HeroGlow"]
    for i in range(3):
        keys(gl, "location", i, frames, [p.loc[i] + (0, -0.012, 0.004)[i] for p in poses])
    keys_scalar(gl.data, "energy", frames, [0.12 * p.glow for p in poses])
    # hero colour: gold outside, the cat's colour for that cell while in the slot
    gold = lin((255, 211, 107))
    hc = []
    for t, p in zip(ts, poses):
        hc.append(lin(ART["states"][A.cat_state(t)][A.HOLE_RC[0]][A.HOLE_RC[1]]) if p.insl else gold)
    for i in range(3):
        f_, v_ = changes(frames, [c[i] for c in hc])
        keys(hero, "color", i, f_, v_, "CONSTANT")

    # paw group + pops
    pg = [A.paw_group(t) for t in ts]
    for i in range(3):
        keys(paw, "location", i, frames, [g[0][i] for g in pg])
    keys(paw, "rotation_euler", 0, frames, [g[1] for g in pg])

    # tiles: colour states + y offsets (pops, ripples)
    states = [A.cat_state(t) for t in ts]
    LG = {k: [[lin(v) for v in row] for row in g] for k, g in ART["states"].items()}
    for (r, c), o in tiles.items():
        cols = [LG[s][r][c] for s in states]
        if any(cc != cols[0] for cc in cols):
            for i in range(3):
                f_, v_ = changes(frames, [cc[i] for cc in cols])
                keys(o, "color", i, f_, v_, "CONSTANT")
        k = [tuple(x) for x in A.PAW_RC].index((r, c)) if (r, c) in [tuple(x) for x in A.PAW_RC] else None
        base_y = 0.0
        ys = []
        for t in ts:
            y = A.ripple_y(t, r, c)
            if k is not None:
                y += A.paw_pop(t, k)
            ys.append(base_y + y)
        active = [i for i, y in enumerate(ys) if abs(y) > 1e-6]
        if active:
            idx = sorted(set(j for i in active for j in (i - 1, i, i + 1) if 0 <= j < N))
            keys(o, "location", 1, [frames[j] for j in idx], [ys[j] for j in idx])
        rots = [A.ripple_rot(t, r, c) for t in ts]
        active = [i for i, (rx, rz) in enumerate(rots) if abs(rx) + abs(rz) > 1e-5]
        if active:
            idx = sorted(set(j for i in active for j in (i - 1, i, i + 1) if 0 <= j < N))
            keys(o, "rotation_euler", 0, [frames[j] for j in idx], [rots[j][0] for j in idx])
            keys(o, "rotation_euler", 2, [frames[j] for j in idx], [rots[j][1] for j in idx])

    # camera
    cam = bpy.data.objects["Cam"]
    cs = [A.camera(t) for t in ts]
    q_prev = None
    qs = []
    for (pos, tgt, lens, foc, fst) in cs:
        q = A.look_quat(pos, tgt)
        if q_prev and sum(a * b for a, b in zip(q, q_prev)) < 0:
            q = tuple(-x for x in q)
        qs.append(q); q_prev = q
    for i in range(3):
        keys(cam, "location", i, frames, [c[0][i] for c in cs])
    for i in range(4):
        keys(cam, "rotation_quaternion", i, frames, [q[i] for q in qs])
    keys_scalar(cam.data, "lens", frames, [c[2] for c in cs])
    fd = []
    for (pos, tgt, lens, foc, fst) in cs:
        fw = Vector(tgt) - Vector(pos); fw.normalize()
        fd.append(max(0.02, (Vector(foc) - Vector(pos)).dot(fw)))
    keys_scalar(cam.data, "dof.focus_distance", frames, fd)
    keys_scalar(cam.data, "dof.aperture_fstop", frames, [c[4] for c in cs])
    # hard cuts must not motion-blur across: step the camera on the cut frames
    for path, n in (("location", 3), ("rotation_quaternion", 4)):
        for i in range(n):
            fc = fcurve_of(cam, path, i)
            for kp in fc.keyframe_points:
                f = int(round(kp.co[0]))
                if any(f == int(round(EV[k] * FPS)) - 1 for k in ("try1", "try2", "try3")):
                    kp.interpolation = "CONSTANT"
    sc.frame_set(0)


def keys_scalar(idd, path, frames, values, interp="LINEAR"):
    owner, attr = (idd.path_resolve(path.rsplit(".", 1)[0]), path.rsplit(".", 1)[1]) if "." in path else (idd, path)
    setattr(owner, attr, values[0])
    idd.keyframe_insert(path, frame=frames[0])
    fc = fcurve_of(idd, path, 0)
    kp = fc.keyframe_points
    kp.add(len(frames) - 1)
    co = []
    for f, v in zip(frames, values):
        co += [f, v]
    kp.foreach_set("co", co)
    for p in kp:
        p.interpolation = interp
    fc.update()


def run(save=True):
    clear_scene()
    setup_render()
    tiles, paw = build_set()
    bake(tiles, paw)
    if save:
        os.makedirs(os.path.join(BASE, "frames"), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=os.path.join(BASE, "pixel_fell_out.blend"))
    print("built", len(tiles), "tiles,", N, "frames; events:", {k: round(v, 2) for k, v in EV.items()})


if globals().get("RUN", True):
    run(globals().get("SAVE", True))
