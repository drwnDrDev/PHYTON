print("Hola mundo con Python")

# Enviar un saludo a la consola desde Python

print("Este es mi saludo desde Python")

# VARIABLES

miVariable = "Hola desde una variable en Python"
print(miVariable)
print(miVariable)
print(miVariable)

name = "Darwin Diaz"
tel = 3132635848
mail = "dwndz@hotmail.com"

# sumar 2 variables

x = 10
y = 2
z = x + y
print(x)
print(y)
print(z)
print("El resultado de la suma es:", z)

# para conocer la dirección de memoria de una veriable se usa la función id():

print(id(x))
print(id(y))
print(id(z))

# muestro el valor de las variables de info personal:

print(name)
print(tel)
print(mail, '\n\n')

# TIPOS DE DATOS EN PYTHON

x = 10
y = 'caracter'
z = True
r = 5.7

print(type(x))  # la funcion type() se usa para mostrar el tipo de dato de una variable.
print(type(y))
print(type(z))
print(type(r))

# concatenar cadenas de texto

miBandaFavorita = "METALLICA"
comentario = "Lo mejor de Rock"
print('La mejor banda del mundo es: ' + miBandaFavorita)  # se unen variables y cadenas usando '+'. Solo realiza una suma cuando la var es tipo int
print('La mejor banda del mundo es: ', miBandaFavorita, comentario)  #Tambien se unen variables y cadenas usando coma','


#TIPO BOOL.......... se usa True y False, teniendo en cuenta que inicia con Mayuscula
print('\nTIPOS BOOLEANOS')

miVariable = 1 < 2
print(miVariable)

if miVariable:
    print("El resultado es Verdadero True")
else:
    print("El resultado es Falso  False")


#Funcion input para procesar la entrada del usuario o sea, para capturar información del usuario
#La funcion input siempre devolvera un valor en tipo de dato str

numero1 = int(input("Ingresa un numero: "))               #se convierte el valor ingresado a int, para poder ejecutar una suma y no una concatenación de str
numero2 = int(input("Ingresa otro numero: "))
resultado = numero1 + numero2

print("El resultado fue: ", resultado)


print("Adios")                                            #El programa no se termina de ejecutar solo hasta que se hacen las operaciones
