#condicion = True

#while condicion:
#    print("Ejecutando ciclo While")
#else:
#    print("FIN del ciclo While")


# contador = 0

# while contador < 3:
  #   print(contador)
  #  contador += 1
# else:
#   print("Fin del ciclo WHILE")


#WHILE DECRECIENTE

'''
minimo = 1
contador = 5

while contador >= minimo:
    print(contador)
    contador -= 1
else:
    print(" Fin del WHILE decreciente")
'''

#CICLO FOR

cadena = 'hola'

for letra in cadena:
    print(letra)
else:
    print('Fin ciclo FOR_1')

#imprimir tabla de multiplicar

numero = int(input('Ingrese un numero de 1 al 10: '))

while 0 < numero <= 10:
    for mult in range(1,11):
        sum = numero * mult
        print(f'{numero} x {mult} = {sum}')
    else:
        print("fin de la operación OK")
    break

else:
    print('Error!!: Debe ser un numero del 1 al 10 \n FIN')





