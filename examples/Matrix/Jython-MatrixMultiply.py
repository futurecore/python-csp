from Jycspthread import *


def calculateRowColumnProduct(A,row,B,col):
    product = 0
    for i in range(len(A[row])):
        product  += A[row][i] * B[i][col]
    return product

@process
def ParcalculateRowColumnProduct(cout,A,row,B,col,width,height, _process=None):
    i = row
    j = col
    res = []
    for i in range((row+width)):
        tmp = []
        for j in range((col+height)):
            tmp.append(calculateRowColumnProduct(A, row, B, col))
        res.append(tmp)
    cout.write((row,col,res))
    
    
        
class Matrix():
    
        def __init__(self,h,k):
            self.matrix = []
            for i in range(h):
                row = []
                for j in range(k):
                    row.append(0)
                    
                self.matrix.append(row)
                    
        

        
        def Multiply(self,mb):
            
            b = mb.matrix
            a = self.matrix
            if len(a[0]) != len(b):
                raise Exception()
                return
            
            mat = Matrix(len(a),len(b[0]))
            for i in range(len(a)) :
                for j in range(len(b[0])):
                    mat.matrix[i][j] = calculateRowColumnProduct(a,i,b,j)
                             
            return mat
        
        def ParMultiply(self,mb,gran):
            
            b = mb.matrix
            a = self.matrix
            if len(a[0]) != len(b):
                raise Exception()
                return
            
            procs = []
            chnls = []
            mat = Matrix(len(a),len(b[0]))
            for i in range((len(a)/gran)) :
                for j in range((len(b[0])/gran)):
                    ch = Channel()
                    chnls.append(ch);
                    procs.append(ParcalculateRowColumnProduct(ch,a,(i*gran),b,(j*gran),gran,gran))
            
          
            p = Par(*procs);
            p.start();   
            
            alt =  Alt(*chnls)
            
            for i in range(len(chnls)):
                a,b,ans = alt.select()
                
                for z in range(len(ans)):
                    for y in range(len(ans[0])):
                        print "co-ord z: " ,z , " y: " , y 
                        mat.matrix[a + z][b + y] = ans[a][b]
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
        i = Matrix(30,30)
        g = Matrix(30,30)
        i.createID()
        g.createID()
        j = i.Multiply(g)
        j.printMatrix();
        j = i.ParMultiply(g,3)
        j.printMatrix()
    
        print ""
