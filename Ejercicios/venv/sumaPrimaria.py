"""
Se te han dado dos listas enlazadas no vacías que representan dos enteros no negativos.
Los dígitos están almacenados en orden inverso, y cada uno de sus nodos contiene un solo dígito.
Suma los dos números y devuelve el resultado como una lista enlazada.
Puedes asumir que los dos números no contienen ningún cero inicial, excepto el número 0 en sí mismo
"""

# l1= [9,9,9,9,9,9,9]
# l2= [9,9,9,9]
l1= [2,2,2]
l2= [1,2,3]
lOutput= []

#print(len(l1))

#i = 0

if len(l1) >= len(l2):
    lista1 = l1
    lista2 = l2
else:
    lista1 = l2
    lista2 = l1

carry = 0

for i in range(min(len(lista1),len(lista2))):
    resTemp = carry + lista1[i] + lista2[i]
    if resTemp >= 10:
        mod = resTemp % 10
        lOutput.append(mod)
        carry=1
    else:
        lOutput.append(resTemp)
        carry=0

print(f'El resultado es: {lOutput}, y la cuenta va en {carry}')


print((len(lista2),len(lista1)))

for i in range(len(lista2),len(lista1)):
    resTemp = carry + lista1[i]
    if resTemp >= 10:
        mod = resTemp % 10
        lOutput.append(mod)
        carry = 1
    else:
        lOutput.append(resTemp)
        carry = 0
        print(f'El resultado es: {lOutput}, y la cuenta va en {carry}')


if carry == 1:
    lOutput.append(carry)
    print(f'El resultado es: {lOutput}, y la cuenta va en {carry}')