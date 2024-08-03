bl_info = {
    "name": "Pudin Simulator",
    "description": "Simulador de pudin mediante el simulador de tela y usando un lenguaje comprensivo.",
    "author": "Estasleyendoesto",
    "blender": (4, 2, 0),
    "category": "Object",
    "version": (1, 2),
    "location": "Tool",
}

import bpy

def calcular_parametros(masa, elasticidad, amortiguacion, inflado_interior, viscosidad, multiplicador):
    # Ajustar parámetros basados en valores físicos y el multiplicador
    tension_stiffness = elasticidad * 10 * multiplicador
    compression_stiffness = elasticidad * 10 * multiplicador
    bending_stiffness = elasticidad * 0.5 * multiplicador
    air_damping = amortiguacion * 0.1 * multiplicador
    viscosidad = viscosidad * multiplicador
    inflado_interior = inflado_interior * multiplicador
    
    return tension_stiffness, compression_stiffness, bending_stiffness, air_damping, inflado_interior, viscosidad

def actualizar_visibilidad_modificadores(obj, show_viewport, show_render):
    cloth = obj.modifiers.get('Cloth')
    smooth = obj.modifiers.get('Pudin Corrective Smooth')
    if cloth:
        cloth.show_viewport = show_viewport
        cloth.show_render = show_render
    if smooth:
        smooth.show_viewport = show_viewport
        smooth.show_render = show_render

class PUDIN_PT_Panel(bpy.types.Panel):
    bl_label = "Pudin Simulator"
    bl_idname = "PUDIN_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        if obj and obj.type == 'MESH':
            cloth = obj.modifiers.get('Cloth')
            if cloth:
                row = layout.row(align=True)
                
                # Corrective Smooth apply
                smooth = obj.modifiers.get('Pudin Corrective Smooth')
                dep = True if smooth else False
                
                row.operator("object.toggle_corrective_smooth", text="Corrective Smooth", depress=dep)
                
                # Render and Viewport Visibility
                cloth = obj.modifiers.get('Cloth')
                render_state = cloth.show_render
                viewport_state = cloth.show_viewport
                
                render_icon_state = 'RESTRICT_RENDER_OFF' if render_state else 'RESTRICT_RENDER_ON'
                viewport_icon_state = 'RESTRICT_VIEW_OFF' if viewport_state else 'RESTRICT_VIEW_ON'
                
                row.operator("object.toggle_viewport_visibility", text="", icon=viewport_icon_state, depress=viewport_state)
                row.operator("object.toggle_render_visibility", text="", icon=render_icon_state, depress=render_state)
                
                # Delete modifiers
                row.operator("object.eliminar_modificador_pudin", text="", icon='X')
                
                # ...
                layout.separator()
                layout.label(text="Pin Group")
                layout.prop_search(cloth.settings, "vertex_group_mass", obj, "vertex_groups", text="")
                
                layout.separator()
                layout.label(text="Simulation")
                layout.prop(cloth.settings, 'quality', text="Calidad de Simulación")
                layout.prop(cloth.collision_settings, 'collision_quality', text="Calidad de Colisión")
                layout.prop(cloth.settings, 'time_scale', text="Velocidad de Simulación")
                layout.prop(cloth.settings.effector_weights, 'gravity', text="Gravedad")
                
                layout.separator()
                layout.label(text="Settings")
                layout.prop(obj, 'pudin_masa', text="Peso")
                layout.prop(obj, 'pudin_elasticidad', text="Elasticidad")
                layout.prop(obj, 'pudin_amortiguacion', text="Amortiguación")
                layout.prop(obj, 'pudin_inflado_interior', text="Inflado")
                layout.prop(obj, 'pudin_viscosidad', text="Viscosidad")
                layout.prop(obj, 'pudin_multiplicador', text="Multiplicador")

                layout.operator("object.aplicar_parametros_pudin", text="Aplicar Parámetros")
                
                layout.separator()
                layout.label(text="Bake")
                
                row = layout.row()
                row.prop(context.scene, 'frame_start', text="Inicio")
                row.prop(context.scene, 'frame_end', text="Fin")
                
                layout.operator("object.hornear_simulacion_pudin", text="Hornear Simulación")         
                layout.operator("object.eliminar_cache_pudin", text="Eliminar Caché")
            else:
                layout.operator("object.aplicar_parametros_pudin", text="Aplicar Simulador")

class OBJECT_OT_AplicarParametrosPudin(bpy.types.Operator):
    bl_label = "Aplicar Parámetros Pudin"
    bl_idname = "object.aplicar_parametros_pudin"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.object
        if obj and obj.type == 'MESH':
            # Añadir la simulación de Cloth si el objeto no la tiene
            if not obj.modifiers.get('Cloth'):
                bpy.ops.object.modifier_add(type='CLOTH')
                obj.pudin_first = True
            
            cloth = obj.modifiers.get('Cloth')
            if cloth:
                masa = obj.pudin_masa
                elasticidad = obj.pudin_elasticidad
                amortiguacion = obj.pudin_amortiguacion
                inflado_interior = obj.pudin_inflado_interior
                viscosidad = obj.pudin_viscosidad
                multiplicador = obj.pudin_multiplicador

                # Guardar los valores originales si es la primera vez
                if obj.pudin_first:
                    obj.pudin_original_elasticidad = elasticidad
                    obj.pudin_original_amortiguacion = amortiguacion
                    obj.pudin_original_inflado_interior = inflado_interior
                    obj.pudin_original_viscosidad = viscosidad
                    obj.pudin_original_masa = masa
                    
                    obj.pudin_first = False
                    
                    # Cambia estos valores la primera vez
                    cloth.settings.tension_stiffness = 5.0
                    cloth.settings.compression_stiffness = 5.0

                    cloth.settings.shear_stiffness_max = 10000.0
                    cloth.settings.bending_stiffness_max = 10000.0
                    cloth.settings.shrink_max = 1.0
                    
                    cloth.settings.effector_weights.force = 0.0
                    cloth.settings.effector_weights.charge = 0.0
                    cloth.settings.effector_weights.texture = 0.0
                    cloth.settings.effector_weights.turbulence = 0.0
                    cloth.settings.effector_weights.drag = 0.45
                
                # Calcular parámetros con el multiplicador sobre los valores originales
                elasticidad = obj.pudin_original_elasticidad
                amortiguacion = obj.pudin_original_amortiguacion
                inflado_interior = obj.pudin_original_inflado_interior
                viscosidad = obj.pudin_original_viscosidad
                
                (tension_stiffness, compression_stiffness, 
                 bending_stiffness, air_damping, inflado_interior, viscosidad) = calcular_parametros(masa, elasticidad, amortiguacion, inflado_interior, viscosidad, multiplicador)
                
                cloth.settings.mass = masa
                
                # Afectan al rendimiento
                # cloth.settings.tension_stiffness = tension_stiffness
                # cloth.settings.compression_stiffness = compression_stiffness
                
                cloth.settings.bending_stiffness = bending_stiffness
                cloth.settings.air_damping = air_damping
                cloth.settings.use_pressure = True
                cloth.settings.uniform_pressure_force = inflado_interior
                cloth.settings.fluid_density = viscosidad

        return {'FINISHED'}

class OBJECT_OT_EliminarModificadorPudin(bpy.types.Operator):
    bl_label = "Eliminar Modificador Pudin"
    bl_idname = "object.eliminar_modificador_pudin"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.object
        if obj and obj.type == 'MESH':
            cloth = obj.modifiers.get('Cloth')
            smooth = obj.modifiers.get('Pudin Corrective Smooth')
            if cloth:
                obj.modifiers.remove(cloth)
                
                obj.pudin_original_masa = 0.3
                obj.pudin_original_elasticidad = 1
                obj.pudin_original_amortiguacion = 1
                obj.pudin_original_inflado_interior = 0
                obj.pudin_original_viscosidad = 0
                
                obj.pudin_masa = 0.3
                obj.pudin_elasticidad = 1
                obj.pudin_amortiguacion = 1
                obj.pudin_inflado_interior = 0
                obj.pudin_viscosidad = 0
                obj.pudin_multiplicador = 1
            if smooth:
                obj.modifiers.remove(smooth)
            
        return {'FINISHED'}

class OBJECT_OT_ToggleCorrectiveSmooth(bpy.types.Operator):
    bl_label = "Toggle Corrective Smooth"
    bl_idname = "object.toggle_corrective_smooth"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.object
        if obj and obj.type == 'MESH':
            smooth = obj.modifiers.get('Pudin Corrective Smooth')
            if smooth:
                obj.modifiers.remove(smooth)
            else:
                smooth = obj.modifiers.new(name='Pudin Corrective Smooth', type='CORRECTIVE_SMOOTH')
        return {'FINISHED'}

class OBJECT_OT_ToggleViewportVisibility(bpy.types.Operator):
    bl_label = "Toggle Viewport Visibility"
    bl_idname = "object.toggle_viewport_visibility"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.object
        if obj and obj.type == 'MESH':
            cloth = obj.modifiers.get('Cloth')
            if cloth:
                new_state = not cloth.show_viewport
                actualizar_visibilidad_modificadores(obj, new_state, cloth.show_render)
        return {'FINISHED'}

class OBJECT_OT_ToggleRenderVisibility(bpy.types.Operator):
    bl_label = "Toggle Render Visibility"
    bl_idname = "object.toggle_render_visibility"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        obj = context.object
        if obj and obj.type == 'MESH':
            cloth = obj.modifiers.get('Cloth')
            if cloth:
                new_state = not cloth.show_render
                actualizar_visibilidad_modificadores(obj, cloth.show_viewport, new_state)
        return {'FINISHED'}

class OBJECT_OT_HornearSimulacionPudin(bpy.types.Operator):
    bl_label = "Hornear Simulación Pudin"
    bl_idname = "object.hornear_simulacion_pudin"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.ptcache.bake_all(bake=True)
        return {'FINISHED'}

class OBJECT_OT_EliminarCachePudin(bpy.types.Operator):
    bl_label = "Eliminar Caché Pudin"
    bl_idname = "object.eliminar_cache_pudin"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        bpy.ops.ptcache.free_bake_all()
        return {'FINISHED'}

def update_original_values(self, context):
    obj = context.object
    if obj and obj.type == 'MESH' and obj.modifiers.get('Cloth'):
        obj.pudin_original_elasticidad = obj.pudin_elasticidad
        obj.pudin_original_amortiguacion = obj.pudin_amortiguacion
        obj.pudin_original_inflado_interior = obj.pudin_inflado_interior
        obj.pudin_original_viscosidad = obj.pudin_viscosidad
        obj.pudin_original_masa = obj.pudin_masa
        context.area.tag_redraw()  # Asegura que la interfaz se actualice

def register():
    bpy.utils.register_class(PUDIN_PT_Panel)
    bpy.utils.register_class(OBJECT_OT_AplicarParametrosPudin)
    bpy.utils.register_class(OBJECT_OT_ToggleViewportVisibility)
    bpy.utils.register_class(OBJECT_OT_ToggleRenderVisibility)
    bpy.utils.register_class(OBJECT_OT_EliminarModificadorPudin)
    bpy.utils.register_class(OBJECT_OT_ToggleCorrectiveSmooth)
    bpy.utils.register_class(OBJECT_OT_HornearSimulacionPudin)
    bpy.utils.register_class(OBJECT_OT_EliminarCachePudin)
    bpy.types.Object.pudin_masa = bpy.props.FloatProperty(
        name="Peso (Masa)", 
        description="Controla el peso del objeto", 
        default=0.3, 
        min=0.0,
        update=update_original_values
    )
    bpy.types.Object.pudin_elasticidad = bpy.props.FloatProperty(
        name="Elasticidad", 
        description="Controla la elasticidad al moverse. 0 = elasticidad máxima. Valores altos hacen vibrar la malla (puede corregirse aumentando la calidad de la simulación y/o aumentando la amortiguación)", 
        default=1.0, 
        min=0.0,
        update=update_original_values
    )
    bpy.types.Object.pudin_amortiguacion = bpy.props.FloatProperty(
        name="Amortiguación", 
        description="Controla cuánto puede comprimirse y estirarse. Valores más altos aumentan la resistencia a la deformación", 
        default=1.0, 
        min=0.0,
        update=update_original_values
    )
    bpy.types.Object.pudin_inflado_interior = bpy.props.FloatProperty(
        name="Inflado Interior", 
        description="Infla el objeto igual que un globo de aire", 
        default=0.0, 
        min=0.0,
        update=update_original_values
    )
    bpy.types.Object.pudin_viscosidad = bpy.props.FloatProperty(
        name="Viscosidad", 
        description="Hace que se comporte como un globo de agua", 
        default=0.0, 
        min=0.0,
        update=update_original_values
    )
    bpy.types.Object.pudin_multiplicador = bpy.props.FloatProperty(
        name="Multiplicador", 
        description="Multiplica los efectos calculados, útil tras subdividir o cambiar el número de polígonos", 
        default=1.0, 
        min=0.1
    )
    bpy.types.Object.pudin_first = bpy.props.BoolProperty(
        name="Enabled",
        default=False,
    )
    bpy.types.Object.pudin_original_masa = bpy.props.FloatProperty(
        name="Masa Original",
        default=0.3
    )
    bpy.types.Object.pudin_original_elasticidad = bpy.props.FloatProperty(
        name="Elasticidad Original",
        default=1.0
    )
    bpy.types.Object.pudin_original_amortiguacion = bpy.props.FloatProperty(
        name="Amortiguación Original",
        default=1.0
    )
    bpy.types.Object.pudin_original_inflado_interior = bpy.props.FloatProperty(
        name="Inflado Interior Original",
        default=0.0
    )
    bpy.types.Object.pudin_original_viscosidad = bpy.props.FloatProperty(
        name="Viscosidad Original",
        default=0.0
    )

def unregister():
    bpy.utils.unregister_class(PUDIN_PT_Panel)
    bpy.utils.unregister_class(OBJECT_OT_AplicarParametrosPudin)
    bpy.utils.unregister_class(OBJECT_OT_ToggleViewportVisibility)
    bpy.utils.unregister_class(OBJECT_OT_ToggleRenderVisibility)
    bpy.utils.unregister_class(OBJECT_OT_EliminarModificadorPudin)
    bpy.utils.unregister_class(OBJECT_OT_ToggleCorrectiveSmooth)
    bpy.utils.unregister_class(OBJECT_OT_HornearSimulacionPudin)
    bpy.utils.unregister_class(OBJECT_OT_EliminarCachePudin)
    del bpy.types.Object.pudin_masa
    del bpy.types.Object.pudin_elasticidad
    del bpy.types.Object.pudin_amortiguacion
    del bpy.types.Object.pudin_inflado_interior
    del bpy.types.Object.pudin_viscosidad
    del bpy.types.Object.pudin_multiplicador
    del bpy.types.Object.pudin_first
    del bpy.types.Object.pudin_original_masa
    del bpy.types.Object.pudin_original_elasticidad
    del bpy.types.Object.pudin_original_amortiguacion
    del bpy.types.Object.pudin_original_inflado_interior
    del bpy.types.Object.pudin_original_viscosidad

if __name__ == "__main__":
    register()