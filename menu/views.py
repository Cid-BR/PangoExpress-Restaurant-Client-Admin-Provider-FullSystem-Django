from django.shortcuts import render, redirect, get_object_or_404

from django.views.generic import View
from django.db import IntegrityError

from .forms import *
#from .models import PERFIL, USUARIO, CLIENTE, PROVEEDOR, PLATO, CUENTA, PedidoEnCuenta
from .models import *

from .BilleteraElectronica import *
import datetime


def index(request):
    all_platos = PLATO.objects.all()
    return render(request, 'menu/slider.html', {'all_platos': all_platos})

def menu(request):
    all_platos = PLATO.objects.all()
    try:
        if(request.session['pid'] != -1):
            perfil = PERFIL.objects.get(id=request.session['pid'])
            usuario = USUARIO.objects.get(perfil=perfil)
            return render(request,'menu/menu.html', {'all_platos' : all_platos, 'usuario':usuario})
        else:
            return render(request, 'menu/menu.html', {'all_platos': all_platos})

    except:
        return render(request, 'menu/menu.html', {'all_platos': all_platos})

        
    


def detail(request, id_plato):
    plato = get_object_or_404(PLATO, pk=id_plato)

    try:
        if(request.session['pid'] != -1):
            perfil = PERFIL.objects.get(id=request.session['pid'])
            usuario = USUARIO.objects.get(perfil=perfil)
            return render(request, 'menu/detail.html', {'plato': plato, 'usuario':usuario})
        else:
            return render(request, 'menu/detail.html', {'plato': plato})
    except:
        return render(request, 'menu/detail.html', {'plato': plato})


''' Formulario general de registro de usuario,
    de aqui redirecciono a cliente o proveedor '''
class FormularioRegistro(View):
    template_name = 'menu/registro.html'

    def get(self, request):
        form = FormRegistrarUsuario()
        form2 = FormRegistrarUsuario2()
        context = {'form' : form, 'form2' : form2 }
        return render(request, self.template_name, context)

    def post(self, request):
        form = FormRegistrarUsuario(request.POST)
        form2 = FormRegistrarUsuario2(request.POST)

        if (form.is_valid() and form2.is_valid()):

            try:
                perfil = form.save()
                request.session['logged'] = True
                request.session['pid'] = perfil.id

                usuario = USUARIO(
                    email=form2.cleaned_data['email'],
                    contrasenia=form2.cleaned_data['contrasenia'],
                    perfil=perfil
                )


                if(form2.cleaned_data['tipo'] == '1'):
                    usuario.es_cliente = True
                    usuario.save()
                    return redirect('/menu/registro/cliente')
                else:
                    usuario.save()
                    return redirect('/menu/registro/proveedor')

            except IntegrityError:
                print("Integrity Error\n")

                request.session['logged'] = False
                request.session['pid'] = -1
                return redirect('/menu/registro/')

        else:
            # Agregar mensaje de error en formulario
            # creo que se puede especificar donde ocurrio el error
            print('Error en formulario\n')

        #return redirect('/menu/registro/')
        return render(request, 'menu/registro.html',{'form': form, 'form2':form2})


''' Formularuio de registro de cliente '''
class FormularioRegistroCliente(View):

    def get(self, request):
        form = FormRegistrarCliente()
        return render(request, 'menu/registroCliente.html', {'form' : form})

    def post(self, request):
        form = FormRegistrarCliente(request.POST)

        if form.is_valid():
            try:
                perfil = PERFIL.objects.get(id=request.session['pid'])
                usuario = USUARIO.objects.get(perfil=perfil)
                cliente = CLIENTE(
                        usuario=usuario,
                        ci=form.cleaned_data['ci'],
                        nombre=form.cleaned_data['nombre'],
                        apellido=form.cleaned_data['apellido'],
                        telefono=form.cleaned_data['telefono'],
                        fechaNacimiento=form.cleaned_data['fechaNacimiento'],
                        billetera_id=None
                        )

                cliente.save()
                return redirect('/menu/')

            except IntegrityError:
                print('marico no lo logra\n')
                return redirect('/menu/registro/cliente')
        else:
            print('formulario invalido\n')
            #return redirect('/menu/registro/cliente')
            return render(request, 'menu/registroCliente.html',{'form': form})



''' Formulario de registro de proveedor'''
class FormularioRegistroProveedor(View):

    def get(self, request):
        form = FormRegistrarProveedor()
        return render(request, 'menu/registroProveedor.html', {'form' : form})

    def post(self, request):
        form = FormRegistrarProveedor(request.POST)

        if form.is_valid():
            try:
                perfil = PERFIL.objects.get(id=request.session['pid'])
                usuario = USUARIO.objects.get(perfil=perfil)
                proveedor = PROVEEDOR(
                        usuario=usuario,
                        rif = form.cleaned_data['rif'],
                        nombre = form.cleaned_data['nombre']
                        )
                proveedor.save()

                return redirect('/menu/')

            except IntegrityError:
                print('marico no lo logra\n')
                return redirect('/menu/registro/proveedor')
        else:
            print('formulario invalido\n')
            return redirect('/menu/registro/proveedor')
            #return render(request, '/menu/registroProveedor.html',{'form': form})


''' Vista de perfil '''
def ver_perfil(request):
    if(request.session.get('logged', default = False)):
        # Obtengo perfil y usuario logeado
        perfil = PERFIL.objects.get(id = request.session['pid'])
        usuario = USUARIO.objects.get(perfil = perfil)
        context = { 'pseudonimo' : perfil.pseudonimo,
                    'email' : usuario.email,
                    'es_cliente' : usuario.es_cliente,
                    'logged' : True
                    }

        if(usuario.es_cliente):
            extra = CLIENTE.objects.get(usuario=usuario)

            context['nombre'] = extra.nombre
            context['apellido'] = extra.apellido
            context['ci'] = extra.ci
            context['telefono'] = extra.telefono
            context['fechaNacimiento'] = extra.fechaNacimiento
        else:
            extra = PROVEEDOR.objects.get(usuario=usuario)

            context['nombre'] = extra.nombre
            context['rif'] = extra.rif
    else:
        context = {'logged' : False}
        print('no iniciaste perro\n')

    return render(request, 'menu/verPerfil.html', context)



''' Edicion de perfil '''
class EditarPerfil(View):

    def get(self, request):

        perfil = PERFIL.objects.get(id=request.session['pid'])
        usuario = USUARIO.objects.get(perfil=perfil)

        if(usuario.es_cliente):
            cliente = CLIENTE.objects.get(usuario = usuario)
            data = {'pseudonimo' : perfil.pseudonimo,
                    'nombre' : cliente.nombre,
                    'apellido': cliente.apellido,
                    'telefono': cliente.telefono
                    }

            form = FormEditarPerfilCliente(data)
        else:
            proveedor = PROVEEDOR.objects.get(usuario = usuario)
            data = {'pseudonimo' : perfil.pseudonimo,
                    'nombre' : proveedor.nombre,
                    'rif' : proveedor.rif
                    }

            form = FormEditarPerfilProveedor(data)

        context = {'form' : form}

        return render(request, 'menu/editarPerfil.html', context)

    def post(self, request):
        perfil = PERFIL.objects.get(id = request.session['pid'])
        usuario = USUARIO.objects.get(perfil=perfil)

        if(usuario.es_cliente):
            cliente = CLIENTE.objects.get(usuario = usuario)
            form = FormEditarPerfilCliente(request.POST)

            if form.is_valid():
                try:
                    perfil.pseudonimo = form.cleaned_data['pseudonimo']
                    perfil.save()
                    cliente.telefono = form.cleaned_data['telefono']
                    cliente.save()
                except IntegrityError:
                    print('Integriry Error\n')
            else:
                print('Error en formulario weon\n')
                return render(request, 'menu/editarPerfil.html',{'form': form})

        else:
            proveedor = PROVEEDOR.objects.get(usuario = usuario)
            form = FormEditarPerfilProveedor(request.POST)

            if form.is_valid():
                try:
                    perfil.pseudonimo = form.cleaned_data['pseudonimo']
                    perfil.save()
                    proveedor.rif = form.cleaned_data['rif']
                    proveedor.save()
                except IntegrityError:
                    print('Integrity Error\n')
            else:
                print('Error en el formulario\n')
                return render(request, 'menu/editarPerfil.html',{'form': form})

        #return render(request, 'editarPerfil',{'form': form})
        return redirect('/menu/perfil')
        #return render(request, '/menu/perfil',{'form': form})


''' Lista todos los clientes registrados en el sistema '''
def ver_clientes(request):
    perfiles = PERFIL.objects.all()
    usuarios = USUARIO.objects.all()
    lista_usuarios = []

    for p in perfiles:
        lista_usuarios.append({ 'pseudonimo' : p.pseudonimo,
                                'passwd' : USUARIO.objects.get(perfil = p).contrasenia,
                                'email' : USUARIO.objects.get(perfil = p).email
                                })

    context = {'lista_usuarios' : lista_usuarios}

    return render(request, 'menu/verClientes.html', context)


''' Muestra formulario de inicio de sesion y hace operaciones
    necesarias para realizar esta accion                     '''
class IniciarSesion(View):

    def get(self, request):
        form = FormIniciarSesion()

        return render(request, 'menu/iniciarSesion.html', {'form' : form })

    def post(self, request):
        form = FormIniciarSesion(request.POST)

        if form.is_valid():
            try:
                perfil = PERFIL.objects.get(pseudonimo = form.cleaned_data['pseudonimo'])
                usuario = USUARIO.objects.get(perfil = perfil)

                if(usuario.contrasenia == form.cleaned_data['passwd']):
                    request.session['logged'] = True
                    request.session['pid'] = perfil.id
                    return redirect('/menu/')

                else:
                    print('No coinciden perrito')
                    request.session['logged'] = False
                    request.session['pid'] = -1
                    return redirect('/menu/iniciarsesion')

            except PERFIL.DoesNotExist:
                print('El perfil no existe')
                request.session['logged'] = False
                request.session['pid'] = -1
                return redirect('/menu/iniciarsesion')


        else:
            print('Error en formulario\n')
            return render(request, '/menu/iniciarsesion',{'form': form})



''' Realiza operaciones necesarias para el cierre de sesion '''
def cerrar_sesion(request):

    request.session['logged'] = False
    request.session['pid'] = -1

    return redirect('/menu/')


''' Crea y asocia a un usuario una billetera electronica '''
def gestionar_billetera(request):
    perfil = PERFIL.objects.get(id = request.session['pid'])
    usuario = USUARIO.objects.get(perfil = perfil)
    cliente = CLIENTE.objects.get(usuario = usuario)

    if cliente.billetera == None:
        return redirect('/menu/perfil/billetera/crear')

    else:
        context = {'nombre': cliente.nombre,
                   'apellido': cliente.apellido,
                   'saldo': cliente.billetera.saldo
                   }
        return render(request, 'menu/mostrarBilletera.html', context)


class CrearBilletera(View):
    def get(self, request):
        perfil = PERFIL.objects.get(id=request.session['pid'])
        usuario = USUARIO.objects.get(perfil=perfil)
        cliente = CLIENTE.objects.get(usuario=usuario)
        data = {'nombre' : cliente.nombre,
                'apellido' : cliente.apellido
                }
        form = FormCrearBilletera(data)
        form.fields['nombre'].widget.attrs['readonly'] = True
        form.fields['apellido'].widget.attrs['readonly'] = True

        return render(request, 'menu/crearBilletera.html', {'form' : form})

    def post(self, request):
        perfil = PERFIL.objects.get(id=request.session['pid'])
        usuario = USUARIO.objects.get(perfil=perfil)
        cliente = CLIENTE.objects.get(usuario=usuario)
        form = FormCrearBilletera(request.POST)

        if form.is_valid():
            try:
                billetera = BILLETERA(nombre = form.cleaned_data['nombre'],
                                      apellido = form.cleaned_data['apellido'],
                                      PIN = form.cleaned_data['PIN'],
                                      saldo = 0
                                      )
                billetera.save()
                cliente.billetera = billetera
                cliente.save()

            except IntegrityError:
                print('Integrity Error\n')

            return redirect('/menu/perfil/billetera/')

        else:
            print("Error en formulario\n")
            return render(request, 'menu/crearBilletera.html', {'form' : form})


''' Formulario de recarga, recarga la billetera '''
class RecargarBilletera(View):
    def get(self, request):
        form = FormRecargaBilletera()

        return render(request, 'menu/recargarBilletera.html', {'form' : form })

    def post(self, request):
        form = FormRecargaBilletera(request.POST)

        if form.is_valid():
            perfil = PERFIL.objects.get(id=request.session['pid'])
            usuario = USUARIO.objects.get(perfil=perfil)
            cliente = CLIENTE.objects.get(usuario=usuario)
            billetera = BilleteraElectronica(ident=cliente.billetera.id,
                                             nombres=cliente.billetera.nombre,
                                             apellidos=cliente.billetera.apellido,
                                             pin=cliente.billetera.PIN,
                                             saldoIni=cliente.billetera.saldo
                                             )

            aux = billetera.recargar(pin=form.cleaned_data['PIN'],
                                     ident=cliente.billetera.id,
                                     ano=datetime.datetime.now().year,
                                     mes=datetime.datetime.now().month,
                                     dia=datetime.datetime.now().day,
                                     monto=form.cleaned_data['monto']
                                     )
            if(aux == 1):
                print('Monto invalido')
                message = 'Monto Invalido'
            elif(aux == 2):
                print('Error en la fecha')
                message = 'Error en la fecha'
            elif(aux == 3):
                print('PIN incorrecto')
                message = 'PIN incorrecto'
            else:
                try:
                    cliente.billetera.saldo = billetera.balance
                    cliente.billetera.save()

                    return redirect('/menu/perfil/billetera/')
                except IntegrityError:
                    print("Integrity Error\n")

            print('fallo la recarga')
            #return redirect('/menu/perfil/billetera/recargar/')
            print(message)
            return render(request, 'menu/recargarBilletera.html', {'form': form,
                                                                   'message': message})

        else:
            print('Eror en el formulario\n')
            return render(request, 'menu/recargarBilletera.html', {'form' : form})


''' Realiza operaciones necesaras para registrar un pedido '''
def hacer_pedido(request, id_plato):
    plato = PLATO.objects.get(id = id_plato)

    perfil = PERFIL.objects.get(id=request.session['pid'])
    usuario = USUARIO.objects.get(perfil=perfil)
    cliente = CLIENTE.objects.get(usuario=usuario)

    try:
        try:
            cuenta = CUENTA.objects.get(cliente = cliente,
                                        pagada = False
                                        )
        except:
            cuenta = CUENTA(cliente = cliente,
                            total = 0,
                            pagada = False
                            )

        pedido = PedidoEnCuenta(plato = plato,
                                cuenta = cuenta
                                )
        if(not PedidoEnCuenta.objects.filter(plato = pedido.plato, cuenta=cuenta).exists()):
            cuenta.total += pedido.plato.precio
            cuenta.save()
            pedido.cantidad = 1
            pedido.save()
        else:
            pedido = PedidoEnCuenta.objects.get(plato = pedido.plato,
                                                cuenta = cuenta)
            cuenta.total += pedido.plato.precio
            pedido.cantidad += 1
            pedido.save()
            cuenta.save()
    except IntegrityError:
        print("Integrity Error\n")

    return redirect('/menu/')

def ver_pedido(request):
    perfil = PERFIL.objects.get(id=request.session['pid'])
    usuario = USUARIO.objects.get(perfil=perfil)

    if(usuario.es_cliente):
        cliente = CLIENTE.objects.get(usuario=usuario)
        try:
            cuenta = CUENTA.objects.get(cliente = cliente,
                                        pagada = False
                                        )
        except:
            cuenta = CUENTA(cliente = cliente,
                            pagada = False
                            )
            cuenta.save()

        pedidos = PedidoEnCuenta.objects.filter(cuenta = cuenta)
        context = {'pedidos' : pedidos, 'cuenta' : cuenta}
    else:
        context = {}

    return render(request, 'menu/verPedido.html', context)

def pagar_cuenta(request, cuenta_id):

    if request.method == 'GET':
        cuenta = CUENTA.objects.get(id = cuenta_id)
        if cuenta.cliente.billetera != None:
            form = FormConfirmacionPIN()
            return render(request, 'menu/pagarCuenta.html', {'form' : form, 'billetera': True})
        else:
            return render(request, 'menu/pagarCuenta.html', {'billetera': False})

    elif request.method == 'POST':
        form = FormConfirmacionPIN(request.POST)

        if form.is_valid():
            cuenta = CUENTA.objects.get(id = cuenta_id)
            perfil = PERFIL.objects.get(id=request.session['pid'])
            usuario = USUARIO.objects.get(perfil=perfil)
            cliente = CLIENTE.objects.get(usuario=usuario)

            billetera = BilleteraElectronica(ident=cliente.billetera.id,
                                             nombres=cliente.billetera.nombre,
                                             apellidos=cliente.billetera.apellido,
                                             pin=cliente.billetera.PIN,
                                             saldoIni=cliente.billetera.saldo
                                             )
            aux = billetera.consumir(pin = form.cleaned_data['PIN'],
                                     ident = cliente.billetera.id,
                                     ano = datetime.datetime.now().year,
                                     mes = datetime.datetime.now().month,
                                     dia = datetime.datetime.now().day,
                                     monto = cuenta.total
                                     )
            if(aux == 0):
                try:
                    cliente.billetera.saldo = billetera.saldo()
                    cliente.billetera.save()
                    trans = TRANSACCION(establecimiento = None,
                                        billetera = cliente.billetera,
                                        tipo = 'Compra',
                                        monto = cuenta.total,
                                        fecha = datetime.datetime.now()
                                        )
                    trans.save()
                    cuenta.pagada = True
                    cuenta.save()

                    return redirect('/menu/verpedido/')
                except IntegrityError:
                    print('IntegrityError\n')

            elif(aux == 1):
                message = 'Fecha invalida'
                print('Fecha invalida')
            elif(aux == 2):
                message = 'Saldo Insuficiente'
                print('Saldo insuficiente')
            elif(aux == 3):
                message = 'Monto invalido'
                print('Monto invalido')
            elif(aux == 4):
                message = 'Pin incorrecto'
                print('Pin incorrecto')
            else:
                print('?')

            #return redirect('/menu/verpedido/')
            return render(request, 'menu/pagarCuenta.html', {'message' : message,
                                                             'billetera' : True,
                                                             'form' : form})

        else:
            print('Formulario invalido')
            return render(request, 'menu/pagarCuenta.html', {'form': form, 'billetera': True})


class VerInventario(View):
    def get(self, request):
        perfil = PERFIL.objects.get(id=request.session['pid'])
        usuario = USUARIO.objects.get(perfil=perfil)
        proveedor = PROVEEDOR.objects.get(usuario=usuario)

        inventario = Ofrece.objects.filter(proveedor = proveedor)

        form = FormAgregarProductoProveedor()

        return render(request, 'menu/verInventario.html', {'form': form, 'inventario': inventario})

    def post(self, request):
        form = FormAgregarProductoProveedor(request.POST)
        perfil = PERFIL.objects.get(id=request.session['pid'])
        usuario = USUARIO.objects.get(perfil=perfil)
        proveedor = PROVEEDOR.objects.get(usuario=usuario)

        if form.is_valid():
            ofrece = Ofrece(proveedor=proveedor,
                            producto = form.cleaned_data['producto'],
                            precio = form.cleaned_data['precio']
                            )
            try:
                ofrece.save()
            except IntegrityError:
                print('IntegrityError\n')
        else:
            print('Formulario invalido')

        return redirect('/menu/perfil/inventario/')

def eliminar_producto_inventario(request, id_ofrece):
    ofrece = Ofrece.objects.get(id=id_ofrece)
    ofrece.delete()

    return redirect('/menu/perfil/inventario/')


''' Dummy para hacer pruebas con el layout '''
def layout_bootstrap(request):

    form = FormRegistrarUsuario()

    return render(request, 'menu/layoutBootstrap.html', {'form' : form })
