package examples.builtins;

import JyCSP.JavaCspChannel;
import JyCSP.Par;
import JyCSP.builtins.*;

public class example4 {


	public static void main(String[] args) {
		JavaCspChannel[] chnls = new JavaCspChannel[] { new JavaCspChannel(),
				new JavaCspChannel(), new JavaCspChannel()};
		Fibonacci f = new Fibonacci(chnls[0]);
		Generator g = new Generator(chnls[1]);
		Multi m = new Multi(chnls[0],chnls[1],chnls[2]);
		Printer p = new Printer(chnls[2]);
		
		Par par = new Par(f,g,m,p);
		par.start();

	}

}
