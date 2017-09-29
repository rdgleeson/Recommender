#recommend.py
#This program takes in two files as command line inputs, a training set and a
#test set. It recommends each user in the test set a list of 5 items based
#off the data in the training set. The third input determines the similarity
#function to use, either cosine or euclidean. Cosine sim is the default.

#Originally used as a recommender for artists

#9/29/17
#Ryan Gleeson

import sys
import math

def jaccard(A,B): #A and B are sets of tuples (artist, recommendation)
    andN = 0
    orN = 0
    flag = 0
    for i in A:
        for j in B:
            if i == j:
                andN+=1
                orN+=1
                flag = 1
        if flag == 0:
            orN+=1
        flag = 0
    for j in B:
        for i in A:
            if i == j:
                flag = 1
        if flag == 0:
            orN+=1
        flag = 0
    return andN/orN

def euclideanSim(person1, person2):
    T = 0
    distance = 0
    for i in person1:
        for j in person2: # i and j are tuples ((str) artist, (int) rating)
            if i[0] == j[0]:
                T+=1
                rd = i[1] - j[1]
                distance+= rd*rd
    if distance == 0:
        return 9999999999
    return T / math.sqrt(distance)

def cosineSim(person1, person2): #cosine sim
    oneRatings = 0
    twoRatings = 0
    bothRatings = 0
    for i in person1:
        oneRatings += i[1]*i[1]
        for j in person2:
            if i[0] == j[0]:
                bothRatings += i[1] * j[1]
    for j in person2:
        twoRatings += j[1]*j[1]
    oneRatings = math.sqrt(oneRatings)
    twoRatings = math.sqrt(twoRatings)
    r = oneRatings * twoRatings
    return bothRatings/r

def averageRating(personData):
    avg = 0
    for i in range(0,len(personData)):
        avg+=personData[i][1]
    return avg/len(personData)
    
def aRt(similar, otherUsers, artist): #Average Rating of artist in top 3 most similar users
    i = 0
    rating = 0
    for j in range(0,3):
        data = otherUsers[similar[j][0]]
        for k in range(0,len(data)):
            if data[k][0] == artist:
                rating += data[k][1]
                i+=1
                break
    if i == 0:
        return 0
    return rating/i
    
def waRt(similar, otherUsers, artist): #Weighted average rating across all users
    z=0
    rating = 0
    for j in range(0,len(similar)):
        data = otherUsers[similar[j][0]]
        for k in range(0,len(data)):
            if data[k][0] == artist:
                rating += similar[j][1]*data[k][1]
                z+=similar[j][1]
                break
    return rating/z
    
def awaRt(similar, otherUsers, artist, avgrt): #Adjusted weighted average rating across all users
    z=0
    rating = 0
    for j in range(0,len(similar)):
        data = otherUsers[similar[j][0]]
        for k in range(0,len(data)):
            if data[k][0] == artist:
                avgrtp = averagerating(data)
                rating += similar[j][1]*(data[k][1] - avgrtp)
                z+=similar[j][1]
                break
    rating = rating / z
    return rating + avgrt
    
def main():
    #Read in the files for recUsers and otherUsers
    artists = []
    jac12 = 0
    jac13 = 0
    jac23 = 0
    recUserFile = open(sys.argv[1], "r")
    recUsers = {}
    count = 0
    for line in recUserFile:
        line = line.split(",")
        if count == 0:  #skip the first line
            count = 1
            continue
        rating = eval(line[2])
        if line[0] in recUsers.keys():
            recUsers[line[0]].append((line[1],rating))
        else:
            recUsers[line[0]] = [(line[1],rating)]
        if line[1] not in artists:
            artists.append(line[1])
    recUserFile.close()            
    otherUserFile = open(sys.argv[2], "r")
    otherUsers = {}
    count = 0
    for line in otherUserFile:
        line = line.split(",")
        if count == 0:
            count = 1
            continue
        rating = eval(line[2])
        if line[0] in otherUsers.keys():
            otherUsers[line[0]].append((line[1],rating))
        else:
            otherUsers[line[0]] = [(line[1],rating)]
        if line[1] not in artists:
            artists.append(line[1])
    otherUserFile.close()
    simType = sys.argv[3]
    #Beginning the comparing process
    f = open("recs.csv", "w")
    f.write("User,Option,Rec1,Rating1,Rec2,Rating2,Rec3,Rating3,Rec4,Rating4,Rec5,Rating5 \n")
    for person in recUsers.keys():
        similar = []
        personData = recUsers[person]
        avgrt = averagerating(personData)
        for person2 in otherUsers.keys():
            simd = 0
            if simType == "E":
                simd = euclideanSim(personData,otherUsers[person2])
            else:
                simd = cosineSim(personData,otherUsers[person2])
            similar.append((person2,simd))
        similar.sort(key=lambda tup: tup[1], reverse=True)
        #The below is for debugging the sim function
##        if person == "User 1":
##            print("User 1", similar[0:4])
##        if person == "User 2":
##            print("User 2", similar[0:4])
##        if person == "User 3":
##            print("User3",similar[0:4])
        recommended1 = []
        recommended2 = []
        recommended3 = []
        for artist in artists:
            done = False
            for i in range(0,len(personData)):
                if personData[i][0] == artist:
                    done = True
            if not done:
                rating1 = aRt(similar, otherUsers, artist)
                rating2 = waRt(similar, otherUsers, artist)
                rating3 = awaRt(similar, otherUsers, artist, avgrt)
                recommended1.append((artist,rating1))
                recommended2.append((artist,rating2))
                recommended3.append((artist,rating3))
        recommended1.sort(key=lambda tup: tup[1], reverse=True)
        recommended2.sort(key=lambda tup: tup[1], reverse=True)
        recommended3.sort(key=lambda tup: tup[1], reverse=True)
        for i in range(1,4):
            f.write(person)
            f.write(",")
            f.write(str(i))
            for j in range(0,4):
                st = ","
                if i == 1:
                    st += recommended1[j][0] + "," + str(recommended1[j][1])
                if i == 2:
                    st += recommended2[j][0] + "," + str(recommended2[j][1])
                if i == 3:
                    st += recommended3[j][0] + "," + str(recommended3[j][1])
                f.write(st)
            st = ","
            if i == 1:
                st += recommended1[5][0] + "," + str(recommended1[5][1]) + "\n"
            if i == 2:
                st += recommended2[5][0] + "," + str(recommended2[5][1]) + "\n"
            if i == 3:
                st += recommended3[5][0] + "," + str(recommended3[5][1]) + "\n"
            f.write(st)
        topFive1 = recommended1[0:5]
        topFive2 = recommended2[0:5]
        topFive3 = recommended3[0:5]
        jac12 += jaccard(topFive1,topFive2)
        jac13 += jaccard(topFive1,topFive3)
        jac23 += jaccard(topFive2,topFive3)
    f.close()
    jac12 = jac12/50
    jac13 = jac13/50
    jac23 = jac23/50
    print("Jaccard 1 and 2: %f" %(jac12))
    print("Jaccard 1 and 3: %f" %(jac13))
    print("Jaccard 2 and 3: %f" %(jac23))
main()
                    
                                                  
                
            
                
    
    
    
