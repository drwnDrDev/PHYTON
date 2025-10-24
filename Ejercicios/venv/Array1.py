# Dado un arreglo de números enteros nums y un número entero target, debes devolver los índices de dos números en el arreglo cuya suma sea igual al target.
# Puedes asumir que cada entrada tiene exactamente una solución, y no puedes usar el mismo elemento dos veces.
# La respuesta puede ser devuelta en cualquier orden. 😊
# Por ejemplo, si tenemos el arreglo nums = [2, 7, 11, 15] y el target es 9, la respuesta sería [0, 1], ya que nums[0] + nums[1] = 2 + 7 = 9.


# nums = input("Insert a list num: ")
# target= int(input("Insert a target: "))
#
# print(f'nums: {nums}')
# print(f'target: {target}')

# nums = [2,6,8,11,19,1,13,5]
# target= 27
#
#
# def buscamarMatch(nums, target):
#     for i in range(len(nums)):
#         for j in range(len(nums)):
#             if nums[i] + nums[j] == target:
#                 return (i, j)
#
# resultado = buscamarMatch(nums, target)
# print(f'Resultado: {resultado}')


class Solution(object):
    def twoSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        for i in range(len(nums)):
            for j in range(len(nums)):
                if (nums[i] + nums[j] == target) and (i!=j):
                    return (i, j)


nums = [3, 2, 4]
target = 6

obj = Solution()
resultado = obj.twoSum(nums, target)

print('Outpout:', resultado)