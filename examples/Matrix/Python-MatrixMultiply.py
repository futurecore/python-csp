#!/usr/bin/env python

# FIXME: Nowhere near PEP8 compatible :(

from csp.cspthread import  *


def calculateRowColumnProduct(self, A, row, B, col):
    product = 0
    for i in range(len(A[row])):
        product  += A[row][i] * B[i][col]
    return product

@process
def ParcalculateRowColumnProduct(cout, A, row, B, col):
    product = 0
    for i in range(len(A[row])):
        product  += A[row][i] * B[i][col]
    cout.write((row,col,product))
        
class Matrix():
    def __init__(self, h, k):
        self.matrix = []
        for i in range(h):
            row = []
            for j in range(k):
                row.append(0)
                    
            self.matrix.append(row)
                    
        def Multiply(self, mb):
            b = mb.matrix
            a = self.matrix
            if len(a[0]) != len(b):
                raise Exception()
                return
            
            mat = Matrix(len(a),len(b[0]))
            for i in range(len(a)) :
                for j in range(len(b[0])):
                    mat.matrix[i][j] = calculateRowColumnProduct(self,a,i,b,j)
                             
            return mat
        
        def ParMultiply(self, mb):
            b = mb.matrix
            a = self.matrix
            if len(a[0]) != len(b):
                raise Exception()
                return
            
            procs = []
            chnls = []
            mat = Matrix(len(a),len(b[0]))
            for i in range(len(a)) :
                for j in range(len(b[0])):
                    ch = Channel()
                    chnls.append(ch);
                    procs.append(ParcalculateRowColumnProduct(ch,a,i,b,j))
            
          
            p = Par(*procs);
            p.start();   
            
            alt =  Alt(*chnls)
            
            for i in range(len(chnls)):
                a,b,ans = alt.select()
                
                mat.matrix[a][b] = ans 
                alt.poison()
                     
            return mat
        
        def createID(self):  
            for i in range(len(self.matrix)) :
                for j in range(len(self.matrix[0])):  
                    if i == j:
                        self.matrix[i][j] = 1
                    else :
                        self.matrix[i][j] = 0
             
        def printMatrix(self):
            print self.matrix
        

if __name__ == '__main__':
    i = Matrix(3,3)
    g = Matrix(3,3)
    i.createID()
    g.createID()
    j = i.Multiply(g)
    j.printMatrix();
    j = i.ParMultiply(g)
    j.printMatrix()
    
    print ""
