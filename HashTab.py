from BitHash import BitHash, ResetBitHash
# import random
from Node import Node


class HashTab(object):
    def __init__(self, size):
        self.__hashArray1 = [None] * (size // 2)  # create 2 arrays, both half the length of size
        self.__hashArray2 = [None] * (size // 2)
        self.__numRecords = 0  # total number of nodes
        self.__size = size  # total size of hash table (both lists)

    # return current number of keys in table
    def __len__(self):
        return self.__numRecords

    def hashFunc(self, s):
        x = BitHash(s)  # hash twice
        y = BitHash(s, x)

        size = self.__size // 2

        return x % size, y % size

    # insert and return true, return False if the key/data is already there,
    # grow the table if necessary
    def insert(self, k, d):
        if self.find(k) is not None: return False  # if already there, return False (no duplicates)

        n = Node(k, d)  # create a new node with key/data

        # increase size of table if necessary
        if self.__numRecords >= (self.__size // 2):
            self.__growHash()

        position1, position2 = self.hashFunc(n.key)  # hash

        # start the loop checking the 1st position in table 1
        pos = position1
        table = self.__hashArray1

        #
        for i in range(5):

            if table[pos] is None:  # if the position in the current table is empty
                table[pos] = n  # insert the node there and return True
                self.__numRecords += 1
                return True

            n, table[pos] = table[pos], n  # else, evict item in pos and insert the item
            # then deal with the displaced node.

            if pos == position1:  # if we're checking the 1st table right now,
                position1, position2 = self.hashFunc(n.key)  # hash the displaced node,
                pos = position2  # and check its 2nd position
                table = self.__hashArray2  # in the 2nd table (next time through loop)
            else:
                position1, position2 = self.hashFunc(n.key)  # otherwise, hash the displaced node,
                pos == position1  # and check the 1st table position.
                table = self.__hashArray1

        self.__growHash()  # grow and rehash if we make it here
        self.rehash(self.__size)
        self.insert(n.key, n.data)  # deal with evicted item

        return True

    # return string representation of both tables
    def __str__(self):
        str1 = "Table 1: [ " + str(self.__hashArray1[0])
        str2 = " Table 2: [ " + str(self.__hashArray2[0])
        for i in range(1, self.__size):
            str1 += ", " + str(self.__hashArray1[i])
        str1 += "]"

        for i in range(1, self.__size):
            str2 += ", " + str(self.__hashArray2[i])
        str2 += "]"

        return str1 + str2

        # get new hash functions and reinsert everything

    def rehash(self, size):
        ResetBitHash()  # get new hash functions

        temp = HashTab(size)  # create new hash tables

        # re-hash each item and insert it into the correct position in the new tables
        for i in range(self.__size // 2):
            x = self.__hashArray1[i]
            y = self.__hashArray2[i]
            if x is not None:
                temp.insert(x.key, x.data)
            if y is not None:
                temp.insert(y.key, y.data)

        # save new tables
        self.__hashArray1 = temp.__hashArray1
        self.__hashArray2 = temp.__hashArray2
        self.__numRecords = temp.__numRecords
        self.__size = temp.__size

    # Increase the hash table's size x 2
    def __growHash(self):
        newSize = self.__size * 2
        # re-hash each item and insert it into the
        # correct position in the new table
        self.rehash(newSize)

    # Return data if there, otherwise return None
    def find(self, k):
        pos1, pos2 = self.hashFunc(k)  # check both positions the key/data
        x = self.__hashArray1[pos1]  # could be in. return data if found.
        y = self.__hashArray2[pos2]
        if x is not None and x.key == k: return x.data
        if y is not None and y.key == k: return y.data

        # return None if the key can't be found
        return None

    # delete the node associated with that key and return True on success
    def delete(self, k):
        pos1, pos2 = self.hashFunc(k)
        x = self.__hashArray1[pos1]
        y = self.__hashArray2[pos2]
        if x is not None and x.key == k:
            self.__hashArray1[pos1] = None
        elif y is not None and y.key == k:
            self.__hashArray2[pos2] = None
        else:
            return False  # the key wasnt found in either possible position
        self.__numRecords -= 1
        return True
