# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# <pep8 compliant>

bl_info = {
    "name": "Shift Keyframes",
    "description": "Shift keyframes left/right via hotkeys",
    "author": "Amaral Krichman",
    "version": (1, 1, 0),
    "blender": (2, 80, 0),
    "location": "Dopesheet/Graph Editor > Key > Transform",
    "warning": "",
    "wiki_url": "",
    "category": "Animation",
}

import bpy
        
        
class GRAPH_OT_keyframe_shift(bpy.types.Operator):
    '''Shift Keyframe'''
    bl_idname = "graph.keyframe_shift"
    bl_label = "Shift Keyframes"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}
    
    #| n of frames to shift | direction to shift them | direction axis (x or y)
    distance: bpy.props.IntProperty(name="Distance", default=1)
    backwards: bpy.props.BoolProperty(name="Backwards", default=False)
    axis: bpy.props.BoolProperty(name="Shift Values instead", default=False)
    vse: bpy.props.BoolProperty(name="VSE Context", default=False)
    
    
    selected = [] 
    
    @classmethod
    def poll(cls, context):
        # add VSE
        if context.preferences.addons[__name__].preferences.global_polling:
            return context.area.type in {'DOPESHEET_EDITOR', 'GRAPH_EDITOR', 'VIEW_3D'}
        else:
            return context.area.type in {'DOPESHEET_EDITOR', 'GRAPH_EDITOR'}
    
       
    def fetch_selected(self):
        self.selected.clear()
        for action in bpy.data.actions:
            for channel in action.fcurves:
                for key in channel.keyframe_points:
                    if key.select_control_point == True:
                        self.selected.append(key)
                        

    def move(self, amount, reverse, axis):
        vmode = bpy.context.preferences.addons[__name__].preferences.vertical_mode
        if vmode == 'ON':
            self.ax = int(axis)
        else:   
            self.ax = 0
            
        for k in self.selected:    
            if not reverse:
                k.co[self.ax] += amount
                if axis and vmode == 'ON':
                    k.handle_left.y += amount
                    k.handle_right.y += amount
                else:
                    k.handle_left.x += amount
                    k.handle_right.x += amount             
            else:
                k.co[self.ax] -= amount
                if axis and vmode == 'ON':
                    k.handle_left.y -= amount
                    k.handle_right.y -= amount
                else:
                    k.handle_left.x -= amount
                    k.handle_right.x -= amount
    
    def execute(self, _context):
        self.fetch_selected()
        self.move(self.distance, self.backwards, self.axis)
        return {'FINISHED'}
    

class GRAPH_MT_keyframe_shift(bpy.types.Menu):
    bl_label = "Shift"
    bl_idname = "GRAPH_MT_keyframe_shift"
         
    def draw(self, _context):
        m = self.layout
        idname = GRAPH_OT_keyframe_shift.bl_idname
        
        r1 = m.operator(idname, text="Forward by 1")
        r1.axis = False
        r1.backwards = False
        r1.distance = 1
        r10 = m.operator(idname, text="Forward by 10")
        r10.axis = False
        r10.distance = 10
        r10.backwards = False
        m.separator()
        l1 = m.operator(idname, text="Backward by 1")
        l1.axis = False
        l1.backwards = True
        l1.distance = 1
        l10 = m.operator(idname, text="Backward by 10")
        l10.axis = False
        l10.backwards = True
        l10.distance = 10


class ShiftKeyframesPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    global_polling: bpy.props.BoolProperty(default=True)
    vertical_mode: bpy.props.EnumProperty(items=[
                                                ('OFF', "Disabled", "", "", 0),
                                                ("ON", "Enabled (experimental)", "", 'ERROR', 1)],
                                                name="Vertical Mode", default='OFF')
    
    
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "global_polling", text="Allow calling the operator in 3D View")
        layout.label(text="Vertical Mode (shift keyframe values too)")
        row = layout.row()
        row.prop(self, "vertical_mode", text="Vertical Mode", expand=True)
    

#---------------------Registration---------------------

def add_menu(self, _context):
    self.layout.menu(GRAPH_MT_keyframe_shift.bl_idname) 

addon_keymaps = []
classes = (GRAPH_OT_keyframe_shift, GRAPH_MT_keyframe_shift, ShiftKeyframesPreferences)



def register():
    
    for c in classes:
        bpy.utils.register_class(c)
    
    bpy.types.GRAPH_MT_key_transform.prepend(add_menu)
    bpy.types.DOPESHEET_MT_key_transform.prepend(add_menu)
        
    kc = bpy.context.window_manager.keyconfigs.addon
    km_1 = kc.keymaps.new(name='Graph Editor', space_type='GRAPH_EDITOR')
    km_2 = kc.keymaps.new(name='Dopesheet', space_type='DOPESHEET_EDITOR')
    km_3 = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
    
    idname = GRAPH_OT_keyframe_shift.bl_idname
    
    
    #Graph------------------------
    kmi_1_R = km_1.keymap_items.new(idname, 'RIGHT_ARROW', 'PRESS', alt=True)
    kmi_1_R.properties.distance = 1    
    kmi_1_R.properties.backwards = False
    kmi_1_R.properties.axis = False

    kmi_1_RR = km_1.keymap_items.new(idname, 'RIGHT_ARROW', 'PRESS', shift=True, alt=True)
    kmi_1_RR.properties.distance = 10
    kmi_1_RR.properties.backwards = False
    kmi_1_RR.properties.axis = False
    
    kmi_1_L = km_1.keymap_items.new(idname, 'LEFT_ARROW', 'PRESS', alt=True)
    kmi_1_L.properties.distance = 1
    kmi_1_L.properties.backwards = True
    kmi_1_L.properties.axis = False
    
    kmi_1_LL = km_1.keymap_items.new(idname, 'LEFT_ARROW', 'PRESS', shift=True, alt=True)
    kmi_1_LL.properties.distance = 10
    kmi_1_LL.properties.backwards = True
    kmi_1_LL.properties.axis = False
    
    kmi_1_U = km_1.keymap_items.new(idname, 'UP_ARROW', 'PRESS', alt=True)
    kmi_1_U.properties.distance = 1
    kmi_1_U.properties.backwards = False
    kmi_1_U.properties.axis = True
    
    kmi_1_UU = km_1.keymap_items.new(idname, 'UP_ARROW', 'PRESS', shift=True, alt=True)
    kmi_1_UU.properties.distance = 10
    kmi_1_UU.properties.backwards = False
    kmi_1_UU.properties.axis = True
    
    kmi_1_D = km_1.keymap_items.new(idname, 'DOWN_ARROW', 'PRESS', alt=True)
    kmi_1_D.properties.distance = 1
    kmi_1_D.properties.backwards = True
    kmi_1_D.properties.axis = True
    
    kmi_1_DD = km_1.keymap_items.new(idname, 'DOWN_ARROW', 'PRESS', shift=True, alt=True)
    kmi_1_DD.properties.distance = 10
    kmi_1_DD.properties.backwards = True
    kmi_1_DD.properties.axis = True
    
    
    #Dopesheet------------------------
    kmi_2_R = km_2.keymap_items.new(idname, 'RIGHT_ARROW', 'PRESS', alt=True)
    kmi_2_R.properties.distance = 1
    kmi_2_R.properties.backwards = False
    kmi_2_R.properties.axis = False
    
    kmi_2_RR = km_2.keymap_items.new(idname, 'RIGHT_ARROW', 'PRESS', shift=True, alt=True)
    kmi_2_RR.properties.distance = 10
    kmi_2_RR.properties.backwards = False
    kmi_2_RR.properties.axis = False
    
    kmi_2_L = km_2.keymap_items.new(idname, 'LEFT_ARROW', 'PRESS', alt=True)
    kmi_2_L.properties.distance = 1
    kmi_2_L.properties.backwards = True
    kmi_2_L.properties.axis = False
    
    kmi_2_LL = km_2.keymap_items.new(idname, 'LEFT_ARROW', 'PRESS', shift=True, alt=True)
    kmi_2_LL.properties.distance = 10
    kmi_2_LL.properties.backwards = True
    kmi_2_LL.properties.axis = False
    
    kmi_2_U = km_2.keymap_items.new(idname, 'UP_ARROW', 'PRESS', alt=True)
    kmi_2_U.properties.distance = 1
    kmi_2_U.properties.backwards = False
    kmi_2_U.properties.axis = True
    
    kmi_2_UU = km_2.keymap_items.new(idname, 'UP_ARROW', 'PRESS', shift=True, alt=True)
    kmi_2_UU.properties.distance = 10
    kmi_2_UU.properties.backwards = False
    kmi_2_UU.properties.axis = True
    
    kmi_2_D = km_2.keymap_items.new(idname, 'DOWN_ARROW', 'PRESS', alt=True)
    kmi_2_D.properties.distance = 1
    kmi_2_D.properties.backwards = True
    kmi_2_D.properties.axis = True
    
    kmi_2_DD = km_2.keymap_items.new(idname, 'DOWN_ARROW', 'PRESS', shift=True, alt=True)
    kmi_2_DD.properties.distance = 10
    kmi_2_DD.properties.backwards = True
    kmi_2_DD.properties.axis = True
    
    # 3D View------------------------
    kmi_3_R = km_3.keymap_items.new(idname, 'RIGHT_ARROW', 'PRESS', alt=True)
    kmi_3_R.properties.distance = 1
    kmi_3_R.properties.backwards = False
    kmi_3_R.properties.axis = False
    
    kmi_3_RR = km_3.keymap_items.new(idname, 'RIGHT_ARROW', 'PRESS', shift=True, alt=True)
    kmi_3_RR.properties.distance = 10
    kmi_3_RR.properties.backwards = False
    kmi_3_RR.properties.axis = False
    
    kmi_3_L = km_3.keymap_items.new(idname, 'LEFT_ARROW', 'PRESS', alt=True)
    kmi_3_L.properties.distance = 1
    kmi_3_L.properties.backwards = True
    kmi_3_L.properties.axis = False
    
    kmi_3_LL = km_3.keymap_items.new(idname, 'LEFT_ARROW', 'PRESS', shift=True, alt=True)
    kmi_3_LL.properties.distance = 10
    kmi_3_LL.properties.backwards = True
    kmi_3_LL.properties.axis = False
    
    kmi_3_U = km_3.keymap_items.new(idname, 'UP_ARROW', 'PRESS', alt=True)
    kmi_3_U.properties.distance = 1
    kmi_3_U.properties.backwards = False
    kmi_3_U.properties.axis = True
    
    kmi_3_UU = km_3.keymap_items.new(idname, 'UP_ARROW', 'PRESS', shift=True, alt=True)
    kmi_3_UU.properties.distance = 10
    kmi_3_UU.properties.backwards = False
    kmi_3_UU.properties.axis = True
    
    kmi_3_D = km_3.keymap_items.new(idname, 'DOWN_ARROW', 'PRESS', alt=True)
    kmi_3_D.properties.distance = 1
    kmi_3_D.properties.backwards = True
    kmi_3_D.properties.axis = True
    
    kmi_3_DD = km_3.keymap_items.new(idname, 'DOWN_ARROW', 'PRESS', shift=True, alt=True)
    kmi_3_DD.properties.distance = 10
    kmi_3_DD.properties.backwards = True
    kmi_3_DD.properties.axis = True
    

    addon_keymaps.append((km_1, km_2, km_3))
    
    
def unregister():
    
    for c in classes:
        bpy.utils.unregister_class(c)
        
    bpy.types.GRAPH_MT_key_transform.remove(add_menu)
    bpy.types.DOPESHEET_MT_key_transform.remove(add_menu)
    

if __name__ == "__main__":
    register()                    