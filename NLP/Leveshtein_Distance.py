def lev(i, j):
    if(min(i,j)==0):
        return max(i,j)
    if(word1[i-1]==word2[j-1]):
        return lev(i-1, j-1)
    return min(lev(i-1,j)+1, lev(i,j-1)+1, lev(i-1,j-1)+1)

word1 = input("Enter word 1:\t")
word2 = input("Enter word 2:\t")

print("Leveshtein Distance:", lev(len(word1), len(word2)))