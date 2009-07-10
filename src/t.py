'''
Created on 22 Jun 2009

'''
import java.lang.Thread as Thread
import java.util.Date as Date

class test(Thread):
    
    def __init__(self, func):
        self._target = func
        #...
        print "Created a Thread called ", self.getName()
        return


    def run(self):
        
        for i in range(10):
            print self.getName() , " ", i    , Date().getTime(), "\n"
        return
        
        
if __name__ == '__main__':
    
    g = test()
    h = test()
    g.start()
    h.start()
    pass