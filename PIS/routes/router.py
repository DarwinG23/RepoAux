from flask import Blueprint, jsonify, abort , request, render_template, redirect, make_response, url_for, flash, Flask
from flask_cors import CORS
from controls.login.cuentaDaoControl import CuentaDaoControl
from controls.administrativo.cursaControl import CursaControl
from controls.usuarios.docenteDaoControl import DocenteControl
from controls.academico.mallaCurricularControl import MallaCurricularControl
from controls.usuarios.estudianteDaoControl import EstudianteControl
from controls.login.personaDaoControl import PersonaDaoControl
from controls.seguimiento.asignacionControl import AsignacionDaoControl
from controls.academico.materiaControl import MateriaControl
from controls.academico.cicloControl import CicloControl
from controls.seguimiento.reporteControl import ReporteControl
from controls.login.rolDaoControl import RolDaoControl
from controls.seguimiento.unidadControl import UnidadControl
from controls.tda.linked.linkedList import Linked_List
from controls.administrativo.periodoAcademicoControl import PeriodoAcademicoControl
import time, math, datetime 
from controls.read_exel.read import Read
from io import BytesIO
from scipy import stats

router = Blueprint('router', __name__)




#CORS(api)
cors = CORS(router, resource={
    r"/*":{
        "origins":"*"
    }
})

#GET: PARA PRESENTAR DATOS
#POST: GUARDA DATOS, MODIFICA DATOS Y EL INICIO DE SESION, EVIAR DATOS AL SERVIDOR

#---------------------------------------------Login-----------------------------------------------------#
@router.route('/', ) #SON GETS
def inicio():
    return render_template('login/login.html')

@router.route('/login',  methods=["POST"])
def login():
    # if idCuenta != "noes" and profe != "noes" and gestor != "noes":
    #     return render_template('login/login.html', idPersona=idCuenta, docente = profe, admin = gestor)
    data = request.form
    cc = CuentaDaoControl()
    cuenta = cc._list().binary_search_models(data["correo"], "_correo")
                       
    if cuenta == -1:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('router.inicio'))
    elif cuenta._contrasenia == data["contrasenia"]:
        pc = PersonaDaoControl()
        listaPersonas = pc._list()
        persona = listaPersonas.binary_search_models(cuenta._idPersona, "_id")
        roles = persona._roles
        
        admin = roles.binary_search_models("Administrador", "_nombre")
        docente = roles.binary_search_models("Docente", "_nombre")
        
        if docente == -1: #si no es docente
            if admin != -1:
                return render_template('header.html', idPersona=persona._id, admin = "admin", docente = "no es")
            return render_template('header.html', idPersona=persona._id, docente = "no es", admin = " ")
        else:
            ac = AsignacionDaoControl()
            listaAsignaciones = ac._list()
            if listaAsignaciones._length != 0:
                arrayasignaciones = listaAsignaciones.lineal_binary_search_models(persona._dni, "_cedula_docente").toArray
            else:
                arrayasignaciones = []
            mc = MateriaControl()
            listaMaterias = Linked_List()
            #recooremos el array de asignaciones
            for i in range(0, len(arrayasignaciones)):
                
                idMateria = arrayasignaciones[i]._id_materia                
                try:
                   materia = mc._list().binary_search_models(idMateria, "_id")
                except:
                    materia = -1

                if materia != -1:
                    listaMaterias.addNode(materia)
                
            if admin != -1:
                return render_template('vista_docente/materias.html', lista = pc.to_dic_lista(listaMaterias), idPersona=persona._id, admin = "admin", docente = "docente")
            
            
            return render_template('vista_docente/materias.html', lista=mc.to_dic_lista(listaMaterias), idPersona=persona._id, admin = "no es", docente = "docente")
    else:
        flash('Contraseña incorrecta', 'error')
        return redirect(url_for('router.inicio'))
    



@router.route('/home/docenteMaterias/<idPersona>/<docente>/<admin>')
def docenteMaterias(idPersona, docente, admin):
    pc = PersonaDaoControl()
    listaPersonas = pc._list()
    persona = listaPersonas.binary_search_models(idPersona, "_id")
        
    ac = AsignacionDaoControl()
    listaAsignaciones = ac._list()
    if listaAsignaciones._length != 0:
        arrayasignaciones = listaAsignaciones.lineal_binary_search_models(persona._dni, "_cedula_docente").toArray
    else:
        arrayasignaciones = []
    mc = MateriaControl()
    listaMaterias = Linked_List()

    for i in range(0, len(arrayasignaciones)):
                
        idMateria = arrayasignaciones[i]._id_materia
  
        materia = mc._list().binary_search_models(idMateria, "_id")

        if materia != -1:
            listaMaterias.addNode(materia)
                    
    return render_template('vista_docente/materias.html',lista = ac.to_dic_lista(listaMaterias), idPersona=idPersona, docente = docente, admin = admin)
 
@router.route('/home')
def home():
    return render_template('header.html')

#/home/{{idPersona}}/{{lista}}
@router.route('/home/<idPersona>/<docente>/<admin>')
def home_id(idPersona, docente, admin):
    return render_template('header.html', idPersona=idPersona, docente = docente, admin = admin)


@router.route('/home/materias/<idPersona>/<docente>/<admin>')
def home_materias(idPersona, docente, admin):
    pc = PersonaDaoControl()
    listaPersonas = pc._list()
    persona = listaPersonas.binary_search_models(int(idPersona), "_id")
    roles = persona._roles
    docente = roles.binary_search_models("Docente", "_nombre")
        
    if docente == -1:
        return render_template('header.html', idPersona=persona._id,docente = docente, admin = admin)
    else:
        ac = AsignacionDaoControl()
        listaAsignaciones = ac._list()
        arrayasignaciones = listaAsignaciones.lineal_binary_search_models(persona._dni, "_cedula_docente").toArray
        mc = MateriaControl()
        listaMaterias = Linked_List()
        #recooremos el array de asignaciones
        for i in range(0, len(arrayasignaciones)):
                
            idMateria = arrayasignaciones[i]._id_materia
  
            materia = mc._list().binary_search_models(idMateria, "_id")

            if materia != -1:
                listaMaterias.addNode(materia)
            
        listaMaterias.print
    
    return render_template('vista_docente/materias.html', lista = pc.to_dic_lista(listaMaterias),idPersona=idPersona, docente = docente, admin = admin)

#VISTA DEL DOCENTE MATERIAS
@router.route('/home/materias')
def ver_materias():
    return render_template('vista_docente/materias.html')


#/home/materias/estudiantes/{{ materia.id }}


@router.route('/home/materias/estudiantes/<idMateria>/<idPersona>/<docente>/<admin>')
def ver_estudiantes(idMateria, idPersona, docente, admin):
    ac = AsignacionDaoControl()
    pc = PersonaDaoControl()
    persona = pc._list().binary_search_models(idPersona, "_id")


    asignaciones = ac._list().lineal_binary_search_models(idMateria, "_id_materia")
    asignaciones = asignaciones.lineal_binary_search_models(persona._dni, "_cedula_docente")
    
    unidades = Linked_List()
    
    pec = PeriodoAcademicoControl()
    periodos = pec._list()
    paralelos = []

    if asignaciones._length != 0:
        alumnos = Linked_List()
        ec = EstudianteControl()
        estudiantes = ec._list().toArray
        idAsignacion = None
        for i in range(0, len(estudiantes)):
            cursas = estudiantes[i]._cursas
            for j in range(0, asignaciones._length):
                cursa = cursas.binary_search_models(asignaciones.getData(j)._id, "_asignacion")
                existe = False

                for unidad in asignaciones.getData(j)._unidades.toArray:
                        if idAsignacion != asignaciones.getData(j)._id:
                            unidades.addLast(unidad)
                        
                idAsignacion = asignaciones.getData(j)._id
                if cursa != -1:
                    for paralelo in paralelos:
                        if paralelo == cursa._paralelo:
                            existe = True
                            break                
                if cursa != -1:
                    if not existe:
                       paralelos.append(cursa._paralelo)
                    alumnos.addNode(estudiantes[i])
        return render_template('vista_docente/alumnos.html', lista=ec.to_dic_lista(alumnos), idPersona=idPersona, idMateria=idMateria, docente = docente, admin = admin, periodos = pec.to_dic_lista(periodos), paralelos = paralelos, unidades = ec.to_dic_lista(unidades))
    else:
        return render_template('login/login.html')
    
@router.route('/home/materias/estudiantes/seguimiento/<idMateria>/<idEstudiante>/<idPersona>/<docente>/<admin>/<idPeriodo>')
def seguimiento(idMateria, idEstudiante, idPersona, docente, admin, idPeriodo):
    

    ec = EstudianteControl()
    pec = PeriodoAcademicoControl()
    cc = CursaControl()

    estudiante = ec._list().binary_search_models(int(idEstudiante), "_id")
    
    ac = AsignacionDaoControl()
    
  
    
    cursas = cc._list().lineal_binary_search_models(idPeriodo, "_periodoAcademico")
    cursas = cursas.lineal_binary_search_models(idEstudiante, "_idEstudiante")
    
    asignacion = None

    for i in range(0, cursas._length):
        idAsignacion = cursas.getData(i)._asignacion
        asignacion  = ac._list().binary_search_models(idAsignacion, "_id")
        if asignacion != -1 and asignacion._id_materia == int(idMateria):
            break
            
    
  
    reportes = Linked_List()
    aprobar = 0
    reprobar = 0
    promedio = 0
    nota_minima = 7
    media = 0
    notas_anteriores = []
    
    if asignacion != -1 or asignacion != None:
        try:
           reportes = asignacion._reportes
        except:
            reportes = Linked_List()
        if reportes._length != 0:
            
            reportes = reportes.lineal_binary_search_models(estudiante._dni, "_cedulaEstudiante")
            
    
            if reportes._length != 0:
                array = reportes.toArray
                for i in range(0, len(array)):
                    promedio += array[i]._nota
                    notas_anteriores.append(array[i]._nota)
                print("\nLO QUE NECESITA\n")
        
                nota_necesaria = nota_minima * int(asignacion._unidades._length) - promedio
                print(nota_necesaria)
                if len(notas_anteriores) == 1:
                    nota_necesaria = nota_necesaria /2
                
                print(nota_necesaria)
                media = promedio / len(notas_anteriores)
                sumatoria_cuadrados = sum((x - media) ** 2 for x in notas_anteriores)
                if len(notas_anteriores) == 1:
                    desviacion_estandar = 0
                    if nota_necesaria <= media:
                        probabilidad_aprobar = 0.9
                        probabilidad_reprobar = 0.1
                    else:
                        probabilidad_aprobar = 0.1
                        probabilidad_reprobar = 0.9
                else:
                    desviacion_estandar = math.sqrt(sumatoria_cuadrados / (len(notas_anteriores) - 1))                          
                    probabilidad_aprobar = 1 - stats.norm.cdf(nota_necesaria, loc=media, scale=desviacion_estandar)
                    probabilidad_reprobar = stats.norm.cdf(nota_necesaria, loc=media, scale=desviacion_estandar)
                    
                aprobar = round(probabilidad_aprobar*100, 2)
                reprobar = round(probabilidad_reprobar * 100, 2)
                
                
           

                unidadPendiente = Linked_List()
                for unidad in asignacion._unidades.toArray:
                    existe = False
                    for reporte in reportes.toArray:
                        if reporte._codigoUnidad == unidad._codigo:
                            existe = True
                            break
                    if not existe:
                        unidadPendiente.addNode(unidad)
                
                
                
                return render_template('vista_docente/seguimiento.html', idEstudiante=idEstudiante, idMateria = idMateria, lista = ec.to_dic_lista(reportes), paprobar = aprobar, preprobar = reprobar, idPersona = idPersona, docente = docente, admin = admin, unidades = ec.to_dic_lista(asignacion._unidades), periodos = pec.to_dic_lista(pec._list()), falta = round(nota_necesaria,2), unidadesPendientes = ec.to_dic_lista(unidadPendiente))
            else:
                return render_template('login/login.html')
        else:
            return render_template('login/login.html')
        
        
#VER LAS UNIDADES DE LA MATERIA DEL DOCENTE
@router.route('/home/materias/estudiantes/unidades/<idMateria>/<idPersona>/<docente>/<admin>')
def ver_unidades_docente(idMateria, idPersona, docente, admin):
    mt = MateriaControl()
    materia = mt._list().binary_search_models(int(idMateria), "_id")
    pc = PersonaDaoControl()
    persona = pc._list().binary_search_models(int(idPersona), "_id")
    cedulaDocente = persona._dni
    dc = DocenteControl()
    docente = dc._list().binary_search_models(cedulaDocente, "_dni")
    materia._asignaciones.print
    if docente == -1:
        return render_template('login/login.html')
    asignacion = materia._asignaciones.binary_search_models(docente._dni, "_cedula_docente")
    unidades = asignacion._unidades
    return render_template('vista_docente/unidades.html', lista=mt.to_dic_lista(unidades), idMateria=idMateria, idPersona=idPersona, docente = docente, admin = admin)
    
@router.route('/home/materias/estudiantes/unidades/agregar/<iPersona>/<idMateria>/<docente>/<admin>')
def agregar_unidades_docente(iPersona, idMateria, docente, admin):
    return render_template('vista_docente/addUnidad.html', idPersona=iPersona, idMateria=idMateria, docente = docente, admin = admin)

#/home/addUnidad/{{idMateria}}/{{idPersona}}/{{docente}}/{{admin}}
@router.route('/home/addUnidad/<idMateria>/<idPersona>/<docente>/<admin>', methods=["POST"])
def addUnidad(idMateria, idPersona, docente, admin):
    pc = PersonaDaoControl()
    persona = pc._list().binary_search_models(int(idPersona), "_id")
    cedula = persona._dni
    
    ac = AsignacionDaoControl()
    
    asignaciones = ac._list().lineal_binary_search_models(int(idMateria), "_id_materia")
    
    asignacionDocente = asignaciones.binary_search_models(cedula, "_cedula_docente")
    
    data = request.form
    
    
    #agregamos la unidad
    uc = UnidadControl()
    uc._unidad._nombre = data["nombre"]
    uc._unidad._estado = True
    uc._unidad._fecha_inicio = data["fecha_inicio"]
    uc._unidad._fecha_limite = data["fecha_limite"]
    uc._unidad._codigo = data["codigo"]
    uc._unidad._numero = data["numero"]
    uc._unidad._asignacion = asignacionDocente._id
    uc.save
    
    
    #agregamos la unidad a la asignacion
    asignacionAux = ac._list().binary_search_models(asignacionDocente._id, "_id")
    asignacionAux._unidades.addLast(uc._unidad)
    ac._asignacion = asignacionAux
    ac.merge(int(asignacionDocente._id)-1)
    
    #agregamos la asignacion a la materia
    mc = MateriaControl()
    materia = mc._list().binary_search_models(idMateria,"_id")
    
    asignacionesMateria = materia._asignaciones
    asignacionesMateria.delete(int(asignacionAux._id)-1)
    asignacionesMateria.addLast(asignacionAux)
    
    materia._asignaciones = asignacionesMateria
    mc._materia = materia

    mc.merge(int(materia._id)-1)
    
    
    return render_template('vista_docente/addUnidad.html', idMateria=idMateria, idPersona=idPersona, docente = docente, admin = admin)
    


#---------------------------------------------Usuarios-----------------------------------------------------#
 
#Lista Docentes
@router.route('/home/docentes/<idPersona>/<docente>/<admin>')
def lista_docente(idPersona, docente, admin):
    dc = DocenteControl()
    list = dc._list()
    return render_template('usuarios/guardarFormularioD.html', lista=dc.to_dic_lista(list), idPersona=idPersona, docente = docente, admin = admin)


#Lista Estudiantes
@router.route('/home/estudiantes/<idPersona>/<docente>/<admin>')
def lista_estudiante(idPersona, docente, admin):
    ec = EstudianteControl()
    list = ec._list()
    return render_template('usuarios/guardarFormularioE.html', lista=ec.to_dic_lista(list), idPersona=idPersona, docente = docente, admin = admin)


#---------------------------------------------Ordenar Usuarios------------------------------------------------------#

@router.route('/home/docentes/<tipo>/<attr>/<metodo>') 
def lista_personas_ordenar_docentes(tipo, attr, metodo):
    dc = DocenteControl()
    
    # E y D - Ordenar
    lista_docentes = dc._list()
    #-----------------------------------------------------#
    lista_docentes.sort_models(attr, int(tipo), int(metodo))
    
    
    return make_response(
        jsonify({"msg": "OK", "code": 200, "data": dc.to_dic_lista(lista_docentes)}),
        200
    )


#---------------------------------------------Busqueda Usuarios------------------------------------------------------#
#"http://localhost:5000/home/docentes/busqueda/"+valor+"/"+atributo

@router.route('/home/docentes/busqueda/<data>/<attr>')
def buscar_docente(data, attr):
    
    dc = DocenteControl()
    list = Linked_List()
    
    if attr == "_nombre" or attr == "_apellido" or attr == "_dni" or attr == "_titulo" or attr == "_cubiculo" or attr == "_idiomas" or attr == "_tipoContrato":
        list = dc._list().lineal_binary_search_models(data, attr)
    else:
        docente = dc._list().binary_search_models(data, attr)
        list.addNode(docente)
    
    
    
    return make_response(
        jsonify({"msg": "OK", "code": 200, "data": dc.to_dic_lista(list)}),
        200
    )

#--------------------------------------------- Modulo - Asignación------------------------------------------------------#
@router.route('/home/asignaciones/<idPersona>/<docente>/<admin>')
def lista_asignacion(idPersona, docente, admin):
    ac  = AsignacionDaoControl()
    list = ac._list()
    return render_template('seguimiento/listaAsignacion.html', lista=ac.to_dic_lista(list), idPersona=idPersona, docente = docente, admin = admin)


@router.route('/seguimiento/unidades/<pos>')
def ver_unidades(pos):
    ac = AsignacionDaoControl()
    unidades = ac._list().getData(int(pos)-1)
    return render_template("seguimiento/unidades.html",  lista = unidades.serializable, idUnidad = pos) 

#Ordenar Asignaciones
@router.route('/home/asignacion/<tipo>/<attr>/<metodo>')
def lista_asignacion_ordenar(tipo, attr, metodo):
    ac = AsignacionDaoControl()
    
    # E y D - Ordenar
    lista_asignaciones = ac._list()
    #-----------------------------------------------------#
    lista_asignaciones.sort_models(attr, int(tipo), int(metodo))
    
    
    return make_response(
        jsonify({"msg": "OK", "code": 200, "data": ac.to_dic_lista(lista_asignaciones)}),
        200
    )
#Buscar Asignaciones
@router.route('/home/asignacion/busqueda/<data>/<attr>')
def buscar_asignacion(data, attr):
    ac = AsignacionDaoControl()
    list = Linked_List()
    
    if attr == "_id_materia" or attr == "_cedula_docente" or attr == "_id":
        asignacion = ac._list().binary_search_models(data, attr)
        list.addNode(asignacion)
    else:
        list = ac._list().lineal_binary_search_models(data, attr)
    
    return make_response(
        jsonify({"msg": "OK", "code": 200, "data": ac.to_dic_lista(list)}),
        200
    )

#EditarAsignacion
@router.route('/home/asignaciones/editar/<idPersona>/<docente>/<admin>', methods=["POST"])
def modificar_asignaciones():
    ac = AsignacionDaoControl()
    data = request.form
    pos = data["id"]
    asignacion = ac._list().getData(int(pos)-1)   


    ac._asignacion = asignacion
    ac._asignacion._id_materia = data["id_materia"]
    ac._asignacion._cedula_docente = data["cedula_docente"]
    ac._asignacion._numero_unidades = data["numero_unidades"]
    ac._asignacion._id_cursa = data["id_cursa"]
  
    ac.merge(int(pos)-1)

    return redirect("/home/asignaciones/editar/<idPersona>/<docente>/<admin>", code=302)


#------------------------------------------------ Cursa-------------------------------------------------------------#

@router.route('/home/cursas/<idPersona>/<docente>/<admin>')
def lista_cursa(idPersona, docente, admin):
    cc  = CursaControl()
    list = cc._list()
    return render_template('administrativo/cursa.html', lista=cc.to_dic_lista(list), idPersona=idPersona, docente = docente, admin = admin)


@router.route('/home/ciclos/<idPersona>/<docente>/<admin>')
def lista_ciclos(idPersona, docente, admin):
    cc  = CicloControl()
    list = cc._list()
    return render_template('academico/ciclos.html', lista=cc.to_dic_lista(list), idPersona=idPersona, docente = docente, admin = admin)

#Ordenar Cursas
@router.route('/home/cursa/<tipo>/<attr>/<metodo>')
def lista_cursa_ordenar(tipo, attr, metodo):
    cc = CursaControl()
    
    # E y D - Ordenar
    lista_cursas = cc._list()
    #-----------------------------------------------------#
    lista_cursas.sort_models(attr, int(tipo), int(metodo))
    
    
    return make_response(
        jsonify({"msg": "OK", "code": 200, "data": cc.to_dic_lista(lista_cursas)}),
        200
    )
#Buscar Cursas
@router.route('/home/cursa/busqueda/<data>/<attr>')
def buscar_cursa(data, attr):
    cc = CursaControl()
    list = Linked_List()
    
    if attr == "_id_materia" or attr == "_cedula_estudiante" or attr == "_id":
        cursa = cc._list().binary_search_models(data, attr)
        list.addNode(cursa)
    else:
        list = cc._list().lineal_binary_search_models(data, attr)
    
    return make_response(
        jsonify({"msg": "OK", "code": 200, "data": cc.to_dic_lista(list)}),
        200
    )

#EditarCursa
@router.route('/home/cursas/editar/<idPersona>/<docente>/<admin>', methods=["POST"])
def modificar_cursas():
    cc = CursaControl()
    data = request.form
    pos = data["id"]
    cursa = cc._list().getData(int(pos)-1)   


    cc._cursa = cursa
    cc._cursa._id_materia = data["id_materia"]
    cc._cursa._cedula_estudiante = data["cedula_estudiante"]
    cc._cursa._nota = data["nota"]
    cc._cursa._asistencia = data["asistencia"]
    cc.merge(int(pos)-1)

    return redirect("/home/cursas/editar/<idPersona>/<docente>/<admin>", code=302)



#--------------------------------------------- Malla - Curricular--------------------------------------------------#

@router.route('/home/mallas/<idPersona>/<docente>/<admin>')
def lista_malla(idPersona, docente, admin):
    mcc = MallaCurricularControl()
    list = mcc._list()
    return render_template('academico/malla.html', lista=mcc.to_dic_lista(list), idPersona=idPersona, docente = docente, admin = admin)


@router.route('/academico/ciclos/<pos>')
def ver_ciclos(pos):
    cc = CicloControl()
    ciclos = cc._list().getData(int(pos)-1)
    return render_template("academico/ciclos.html",  lista = ciclos.serializable, idCiclos = pos)


@router.route('/academico/ciclos/<pos>/<idPersona>/<docente>/<admin>')
def ver_ciclos_malla(pos, idPersona, docente, admin):
    mc = MallaCurricularControl()
    malla = mc._list().getData(int(pos)-1)
    ciclos = malla._ciclos
    return render_template("academico/ciclos.html",  lista = mc.to_dic_lista(ciclos), idCiclos = pos, idPersona= idPersona, docente = docente, admin = admin)  


#Ordenar Malla Curricular
@router.route('/home/malla/<tipo>/<attr>/<metodo>')
def lista_malla_ordenar(tipo, attr, metodo):
    mcc = MallaCurricularControl()
    
    # E y D - Ordenar
    lista_malla = mcc._list()
    #-----------------------------------------------------#
    lista_malla.sort_models(attr, int(tipo), int(metodo))
    
    
    return make_response(
        jsonify({"msg": "OK", "code": 200, "data": mcc.to_dic_lista(lista_malla)}),
        200
    )
#Buscar Malla Curricular
@router.route('/home/malla/busqueda/<data>/<attr>')
def buscar_malla(data, attr):
    
    mcc = MallaCurricularControl()
    list = Linked_List()
   
    if attr == "_nombre" or attr == "_descripcion" or attr == "_vigencia":
        malla = mcc._list().binary_search_models(data, attr)
        list.addNode(malla)
    else:
        list = mcc._list().lineal_binary_search_models(data, attr)
    
    return make_response(
        jsonify({"msg": "OK", "code": 200, "data": mcc.to_dic_lista(list)}),
        200
    )

#Malla - Editar

@router.route('/home/mallas/editarRender/<pos>/<idPersona>/<docente>/<admin>', methods=["POST"])
def modificar_mallas_render(pos, idPersona, docente, admin):
    return render_template('academico/editarMalla.html', idPersona=idPersona, docente = docente, admin = admin, pos = pos)

@router.route('/home/mallas/editar/<pos>/<idPersona>/<docente>/<admin>', methods=["POST"])
def modificar_mallas(pos, idPersona, docente, admin):
    mcc = MallaCurricularControl()
    data = request.form
    pos = data["id"]
    malla = mcc._list().getData(int(pos)-1)   

    #TODO ...Validar
    mcc._mallaCurricular = malla
    mcc._mallaCurricular._nombre = data["nombre"]
    mcc._mallaCurricular._descripcion = data["descripcion"]
    mcc._mallaCurricular._vigencia = data["vigencia"]   
    mcc.merge(int(pos)-1)

    return render_template("academico/malla.html", idPersona=idPersona, docente = docente, admin = admin)

#---------------------------------------------Ordenar -  Materia--------------------------------------------------#

@router.route('/home/listamaterias/<idPersona>/<docente>/<admin>')
def lista_materia(idPersona, docente, admin):
    mc  = MateriaControl()
    list = mc._list()
    return render_template('academico/materia.html', lista=mc.to_dic_lista(list), idPersona=idPersona, docente = docente, admin = admin)


#Ordenar
@router.route('/home/materia/<tipo>/<attr>/<metodo>')
def lista_materia_ordenar(tipo, attr, metodo):
    mc = MateriaControl()

    lista_materias = mc._list()
    #-----------------------------------------------------#
    lista_materias.sort_models(attr, int(tipo), int(metodo))
    
    
    return make_response(
        jsonify({"msg": "OK", "code": 200, "data": mc.to_dic_lista(lista_materias)}),
        200
    )

#Buscar
@router.route('/home/materia/busqueda/<data>/<attr>')
def buscar_materia(data, attr):
    mc = MateriaControl()
    list = Linked_List()
    
    if attr == "_nombre" or attr == "_codigo" or attr == "_horas":
        list = mc._list().lineal_binary_search_models(data, attr)
    else:
        materia = mc._list().binary_search_models(data, attr)
        list.addNode(materia)
    
    return make_response(
        jsonify({"msg": "OK", "code": 200, "data": mc.to_dic_lista(list)}),
        200
    )


#----------------------------------------------  Rol --------------------------------------------------#

@router.route('/home/rol/<idPersona>/<docente>/<admin>')
def lista_rol(idPersona, docente, admin):
    rdc = RolDaoControl()
    list = rdc._list()
    list.print
    return render_template('login/rol.html', lista=rdc.to_dic_lista(list), idPersona=idPersona, docente = docente, admin = admin)

#Ordenar
@router.route('/home/rol/<tipo>/<attr>/<metodo>')
def lista_rol_ordenar(tipo, attr, metodo):
    rdc = RolDaoControl()
    
    # E y D - Ordenar
    lista_roles = rdc._list()
    #-----------------------------------------------------#
    lista_roles.sort_models(attr, int(tipo), int(metodo))
    
    
    return make_response(
        jsonify({"msg": "OK", "code": 200, "data": rdc.to_dic_lista(lista_roles)}),
        200
    )
    
#   #agrega todoas las unidades que ha tenido la materia en todos sus periodos academicos
#                 for unidadesAux in asignaciones.getData(j)._unidades:
#                     for unidad in unidadesAux:
#                         if unidad._estado == True:
#                             unidades.addLast(unidad)

#Buscar
@router.route('/home/rol/busqueda/<data>/<attr>')
def buscar_rol(data, attr):
    rdc = RolDaoControl()
    list = Linked_List()
    
    if attr == "_nombre" or attr == "_descripcion" or attr == "_estado":
        list = rdc._list().lineal_binary_search_models(data, attr)
    else:
        rol = rdc._list().binary_search_models(data, attr)
        list.addNode(rol)
    
    return make_response(
        jsonify({"msg": "OK", "code": 200, "data": rdc.to_dic_lista(list)}),
        200
    )


#---------------------------------------------Ordenar -  Unidad--------------------------------------------------------#

@router.route('/home/unidades/<idPersona>/<docente>/<admin>')
def lista_unidad(idPersona, docente, admin):
    uc = UnidadControl()
    list = uc._list()
    return render_template('seguimiento/unidades.html', lista=uc.to_dic_lista(list), idPersona=idPersona, docente = docente, admin = admin)

#---------------------------------------------Lista - Personas --------------------------------------------------------#
@router.route('/home/personas/ver/<idPersona>/<docente>/<admin>')
def ver_lista_personas( idPersona, docente, admin):
    pc = PersonaDaoControl()
    list = pc._list()
    return render_template('login/listaPersona.html', lista=pc.to_dic_lista(list), idPersona=idPersona, docente = docente, admin = admin)


@router.route('/login/rol/<pos>/')
def ver_roles(pos):
    rdc = RolDaoControl()
    rol = rdc._list().getData(int(pos)-1)
    return render_template("login/rol.html",  lista = rol.serializable, idRol = pos) 

#Ordenar

@router.route('/home/personas/ordenar/<tipo>/<attr>/<metodo>')
def lista_personas_ordenar(tipo, attr, metodo):
    pc = PersonaDaoControl()
    lista_personas = pc._list()
    lista_personas.sort_models(attr, int(tipo), int(metodo))

    return make_response(
        jsonify({"msg": "OK", "code": 200, "data": pc.to_dic_lista(lista_personas)}),
        200
    )

#Buscar
@router.route('/home/personas/busqueda/<data>/<attr>')
def buscar_personas(data, attr):
    pc = PersonaDaoControl()
    list = Linked_List()
    
    if attr == "_nombre" or attr == "_apellido" or attr == "_dni" or attr == "_idCuenta:":
        list = pc._list().lineal_binary_search_models(data, attr)
    else:
        persona = pc._list().binary_search_models(data, attr)
        list.addNode(persona)
    
    return make_response(
        jsonify({"msg": "OK", "code": 200, "data": pc.to_dic_lista(list)}),
        200
    )



@router.route('/home/personas/agregar/<idPersona>/<docente>/<admin>')
def ver_personas(idPersona, docente, admin):
    return render_template('usuarios/personas.html', idPersona=idPersona, docente = docente, admin = admin)


@router.route('/home/personas/formularios/guardar', methods=["POST"])
def guardar_registro():
    pc = PersonaDaoControl()
    dc = DocenteControl()
    ec = EstudianteControl()
    data = request.form
    
    if not "apellidos" in data.keys():
        abort(400)
        
    # Validar y guardar datos comunes a todas las personas
    pc._persona._dni = data["dni"]
    pc._persona._nombre = data["nombre"]
    pc._persona._apellido = data["apellido"]
    pc._persona._fechaNacimiento = data["fechaNacimiento"]
    pc._persona._numTelefono = data["numTelefono"]
    pc.save()

    # Guardar datos específicos dependiendo del rol
    if data["rol"] == "docente":
        dc._docente._titulo = data["titulo"]
        dc._docente._cubiculo = data["cubiculo"]
        dc._docente._idiomas = data["idiomas"]
        dc._docente._tipoContrato = data["tipoContrato"]
        dc.save()

    elif data["rol"] == "estudiante":
        ec._estudiante._nota = data["nota"]
        ec._estudiante._asistencia = data["asistencia"]
        ec._estudiante._colegioProcedencia = data["colegioProcedencia"]
        ec.save()

    # Redireccionar según el rol
    if data["rol"] == "docente":
        return redirect("/usuarios/guardarFormulariosD", code=302)
    elif data["rol"] == "estudiante":
        return redirect("/usuarios/guardarFormulariosE", code=302)
    else:
        abort(400) 



@router.route('/personas/modificar', methods=["POST"])
def modificar_personas():
    pc = PersonaDaoControl()
    dc = DocenteControl()
    ec = EstudianteControl()

    data = request.form
    pos = data["id"]
    personas = pc._list().get(int(pos)-1)
    if not "apellido" in data.keys():
        abort(400)
        
    # Validaciones básicas
    if "rol" not in data:
        abort(400)

    # Actualizar datos comunes a todas las personas
    pc._persona = personas
    pc._persona._dni = data["cedula"]
    pc._persona._nombre = data["nombre"]
    pc._persona._apellido = data["apellido"]
    pc._persona._fechaNacimiento = data["fechaNacimiento"]
    pc._persona._numTelefono = data["numTelefono"]
    pc.merge(int(pos)-1)

    # Actualizar datos específicos dependiendo del rol
    role = data["rol"]
    if role == "Docente":
        dc._docente = personas
        dc._docente._titulo = data["titulo"]
        dc._docente._cubiculo = data["cubiculo"]
        dc._docente._idiomas = data["idiomas"]
        dc._docente._tipoContrato = data["tipoContrato"]
        dc.merge(int(pos)-1)

    
    elif role == "Estudiante":
        ec._estudiante = personas
        ec._estudiante._nota = data["nota"]
        ec._estudiante._asistencia = data["asistencia"]
        ec._estudiante._colegioProcedencia = data["colegioProcedencia"]
        ec.merge(int(pos)-1)
    
    return redirect("/personas", code=302)


@router.route('/personas/eliminar', methods=["POST"])
def eliminar_personas():
    pc = PersonaDaoControl()
    pos = request.form["id"]
    pc._delete(int(pos)-1)

    dc = DocenteControl()
    dc._delete(int(pos)-1)

    ec = EstudianteControl()
    ec._delete(int(pos)-1)


    return redirect("/personas", code=302)


#/home/materias/estudiantes/filtrar/"+periodo+"/"+paralelo+"/"+nota+"/"+matricula+"/"+idMateria+"/"+idPersona+"/"+docente+"/"+admin
@router.route('/home/materias/estudiantes/filtrar/<periodo>/<paralelo>/<nota>/<matricula>/<idMateria>/<idPersona>/<docente>/<admin>/<idUnidad>')
def filtrar_estudiantes(periodo, paralelo, nota, matricula, idMateria, idPersona, docente, admin, idUnidad):
    print("\n\n FILTRANDO  \n\n")
    ac = AsignacionDaoControl()
    pc = PersonaDaoControl()
    uc = UnidadControl()
    rc = ReporteControl()
    persona = pc._list().binary_search_models(idPersona, "_id")
    
    print(persona)
    
    asignaciones = ac._list().lineal_binary_search_models(int(idMateria), "_id_materia")
    asignaciones = asignaciones.lineal_binary_search_models(persona._dni, "_cedula_docente")
    
    asignaciones.print
    unidad = uc._list().binary_search_models(int(idUnidad), "_id")

    try:
        reportes = rc._list().lineal_binary_search_models(unidad._codigo, "_codigoUnidad")
    except:
        reportes = Linked_List()
    pec = PeriodoAcademicoControl()
    paralelos = []
    print("length: ", asignaciones._length)
    if asignaciones._length != 0:
        print("\n HAY ASIGNACIONES  \n")
        alumnos = Linked_List()
        ec = EstudianteControl()
        estudiantes = ec._list().toArray
        print(len(estudiantes))
        for i in range(0, len(estudiantes)):
            cursas = estudiantes[i]._cursas
            for j in range(0, asignaciones._length):
                
                cursa = cursas.binary_search_models(asignaciones.getData(j)._id, "_asignacion")
                existe = False
                
                
                for par in paralelos:
                    if par == cursa._paralelo:
                        existe = True
                        break
                                    
                if cursa != -1:
                    if not existe:
                       paralelos.append(cursa._paralelo)
                    
                    try:
                        auxParalelo = int(paralelo)
                    except:
                        auxParalelo = paralelo
                    
                    if int(periodo) != 0 and auxParalelo != 0:
                        print("\n\n FILTRANDO POR PERIODO \n\n")
                        if int(cursa._periodoAcademico) == int(periodo) and str(paralelo).lower() == str(cursa._paralelo).lower():
                            alumnos.addNode(estudiantes[i])
                    elif int(periodo) != 0 and auxParalelo == 0:
                        if int(cursa._periodoAcademico) == int(periodo):
                            alumnos.addNode(estudiantes[i])
                            
                    elif int(periodo) == 0 and auxParalelo != 0:
                        if str(paralelo).lower() == str(cursa._paralelo).lower():
                            alumnos.addNode(estudiantes[i])
                    else:
                        alumnos.addNode(estudiantes[i])
                 

    alumnos.print            
                
                        
    #Filtro por nota
    if int(nota) != 0:
        auxAlumnos = []
        for i in range(0, alumnos._length):
            alumno = alumnos.getData(i)
            if reportes._length != 0:
               reporte = reportes.binary_search_models(alumno._dni, "_cedulaEstudiante")
            else:
                reporte = -1
            if reporte != -1 and float(reporte._nota) < float(nota):

                auxAlumnos.append(alumno)
        alumnos.clear
        
        for i in range(0, len(auxAlumnos)):
            alumnos.addNode(auxAlumnos[i])
            
    #Filtro por matricula
    if int(matricula) != 0:
        auxAlumnos = []
        for i in range(0, alumnos._length):
            alumno = alumnos.getData(i)
            if reportes._length != 0:
               reporte = reportes.binary_search_models(alumno._dni, "_cedulaEstudiante")
            else:
                reporte = -1
            if reporte != -1 and int(reporte._numMatricula) == int(matricula):
                auxAlumnos.append(alumno)
        alumnos.clear
        
        for i in range(0, len(auxAlumnos)):
            alumnos.addNode(auxAlumnos[i])
    
    return make_response(
        jsonify({"msg": "OK", "code": 200, "data": pec.to_dic_lista(alumnos)}),
        200
    )
    

#/home/materias/estudiantes/unidades/notas/{{idMateria}}/{{idPersona}}/{{docente}}/{{admin}}
@router.route('/home/materias/estudiantes/unidades/notas/<idMateria>/<idPersona>/<docente>/<admin>')
def subir_notas(idMateria, idPersona, docente, admin):
    return render_template('vista_docente/notas.html',  idMateria=idMateria, idPersona=idPersona, docente = docente, admin = admin)

#/home/subirNotas/{{idMateria}}/{{idPersona}}/{{docente}}/{{admin}}
@router.route('/home/subirNotas/<idMateria>/<idPersona>/<docente>/<admin>', methods=["POST"])
def cargar_archivo(idMateria, idPersona, docente, admin):
    if 'url' in request.files:
        archivo = request.files['url']
        if archivo.filename != '':
            # Crear una instancia de Read con el archivo cargado
            archivo_bytes = BytesIO(archivo.read())  # Leer el archivo en memoria
            r = Read(archivo_bytes)
            r.leer_archivo()
            r.imprimir()
            tabla = r.info_to_dict()
            
     
    pec = PeriodoAcademicoControl()
    periodos = pec._list()
    
    peridoActual = None 
    for i in range(0, periodos._length):
        fechaFin = periodos.getData(i)._fecha_fin
        #transforma a data time en dia mes año
        fechaFin = datetime.datetime.strptime(fechaFin, '%d/%m/%Y')
        for j in range(0, periodos._length):
            fecha_inicio = periodos.getData(j)._fecha_inicio
            fecha_inicio = datetime.datetime.strptime(fecha_inicio, '%d/%m/%Y')
            if fecha_inicio > fechaFin or fecha_inicio == fechaFin:
                peridoActual = periodos.getData(j)
    
    
    
    ac = AsignacionDaoControl()
    pc = PersonaDaoControl()
    persona = pc._list().binary_search_models(idPersona, "_id")


    asignaciones = ac._list().lineal_binary_search_models(idMateria, "_id_materia")
    asignaciones = asignaciones.lineal_binary_search_models(persona._dni, "_cedula_docente")
    
    unidades = Linked_List()
    
    paralelos = []

    if asignaciones._length != 0:
        ec = EstudianteControl()
        estudiantes = ec._list().toArray
        idAsignacion = None
        for i in range(0, len(estudiantes)):
            cursas = estudiantes[i]._cursas
            for j in range(0, asignaciones._length):
                cursa = cursas.binary_search_models(asignaciones.getData(j)._id, "_asignacion")
                existe = False

                for unidad in asignaciones.getData(j)._unidades.toArray:
                        if idAsignacion != asignaciones.getData(j)._id:
                            unidades.addLast(unidad)
                        
                idAsignacion = asignaciones.getData(j)._id
                if cursa != -1:
                    for paralelo in paralelos:
                        if paralelo == cursa._paralelo:
                            existe = True
                            break                
                if cursa != -1:
                    if not existe:
                       paralelos.append(cursa._paralelo)
                    
    
    
    return render_template('vista_docente/notas.html',  idMateria=idMateria, idPersona=idPersona, docente = docente, admin = admin, tabla = tabla, paralelos = paralelos, unidades = ec.to_dic_lista(unidades), periodo = peridoActual._id)


#"/home/notas/{{idMateria}}/{{idPersona}}/{{docente}}/{{admin}}"
@router.route('/home/notas/<idMateria>/<idPersona>/<docente>/<admin>/<tabla>/<idPeriodo>', methods=["POST"])
def verificar_exel(idMateria, idPersona, docente, admin, tabla, idPeriodo):

    print("\n\nVERIFICANDO EXEL\n\n")
    
    data = request.form
    unidad = data["unidad"]
    paralelo = data["paralelo"]

    unidad = UnidadControl()._list().binary_search_models(unidad, "_id")
    materia = MateriaControl()._list().binary_search_models(idMateria, "_id")

    r = Read(None)
    tabla = r.str_to_dict(tabla)
    ac = AsignacionDaoControl()
    pc = PersonaDaoControl()
    profesor = pc._list().binary_search_models(idPersona, "_id")
    periodo = PeriodoAcademicoControl()._list().binary_search_models(int(idPeriodo), "_id")
    
    asignaciones = ac._list().lineal_binary_search_models(idMateria, "_id_materia")
    asignacion = asignaciones.binary_search_models(profesor._dni, "_cedula_docente")


    
    idEstudiantes = []
    
    cursas = asignacion._cursas
    print("Asignacion")
    print(asignacion)
    print("Cursas")
    print(cursas._length)
    for i in range(0, cursas._length): 
        cursa = cursas.getData(i)
        print("Comprobando")
        print(cursa._paralelo)
        print(paralelo)
        print(cursa._periodoAcademico)
        print(periodo._id)
        if cursa._paralelo == paralelo: #and cursa._periodoAcademico == periodo._id:
            idEstudiantes.append(cursa._idEstudiante)
            
   
    for i in range(0, len(idEstudiantes)):
        existe = False
        reporteExiste = False
        estudante = EstudianteControl()._list().binary_search_models(idEstudiantes[i], "_id")
        for registro in tabla:
            cedula = registro['cedula']
            nota = registro['notas']
            if estudante._dni == cedula:
                existe = True
                break
        if existe:
            print("El estudiante existe")
            rec = ReporteControl()
            reportes = rec._list()
            for j in range(0, reportes._length):
                reporte = reportes.getData(j)
                if reporte._cedulaEstudiante == cedula and reporte._codigoUnidad == unidad._codigo  and reporte._codigoMateria == materia._codigo:
                    print("El reporte existe")
                    reporteExiste = True
                    break
            
            if not reporteExiste:
                cursasEstudiante = cursas.lineal_binary_search_models(idEstudiantes[i], "_idEstudiante")
                cursaArr = []
                
                for i in range (0, asignaciones._length):
                    for j in range(0, cursasEstudiante._length):
                        if asignaciones.getData(i)._id == cursasEstudiante.getData(j)._asignacion:
                            cursaArr.append(cursasEstudiante.getData(j))
                
                rec._reporte._cedulaEstudiante = cedula
                rec._reporte._codigoUnidad = unidad._codigo
                rec._reporte._codigoMateria = materia._codigo
                rec._reporte._nota = nota
                rec._reporte._numMatricula = len(cursaArr)
                rec._reporte._asistencia = 100
                rec._reporte._idAsignacion = asignacion._id
                rec.save
                print("Reporte Datos")
                print("cedula: ", rec._reporte._cedulaEstudiante)
                print("codigoUnidad: ", rec._reporte._codigoUnidad)
                print("codigoMateria: ", rec._reporte._codigoMateria)
                print("nota: ", rec._reporte._nota)
                print("numMatricula: ", rec._reporte._numMatricula)
                print("asistencia: ", rec._reporte._asistencia)
                print("idAsignacion: ", rec._reporte._idAsignacion)
                
                # rec.save
                # asignacion._reportes.print
                # reportes.addNode(rec._reporte)
                # asignacion._reportes.addNode(rec._reporte)
                # ac._asignacion = asignacion
                # ac.merge(int(asignacion._id)-1)
                
                
        else:
            print("El estudiante no Existe")
            
            
        

    
    return redirect("/home/materias/estudiantes/unidades/notas/"+idMateria+"/"+idPersona+"/"+docente+"/"+admin, code=302)