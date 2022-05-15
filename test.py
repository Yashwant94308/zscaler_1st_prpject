ffff = []
def pre(a):
	n = len(a)
	prefixSum = [0 for i in range(n +1)]
	prefixSum[0] = arr[0]
	for i in range(1, n):
		prefixSum[i] = prefixSum[i - 1] + arr[i]
	s = 0
	for i in range(len(prefixSum)):
		s += ((-1)**(i)*prefixSum[i])
	print(s)


def permute(a, l, r):
    if l==r:
        pre(a)
    else:
        for i in range(l,r):
            a[l], a[i] = a[i], a[l]
            permute(a, l+1, r)
            a[l], a[i] = a[i], a[l] 


arr = [3,4,5,1,1]
permute(arr, 0, len(arr))
