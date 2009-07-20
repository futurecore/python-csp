package examples.builtins;

import JyCSP.JavaCspChannel;
import JyCSP.builtins.Fibonacci;
import JyCSP.builtins.Succ;

public class example2 {
	/**
	 * @param args
	 */
	public static void main(String[] args) {
		JavaCspChannel c1 = new JavaCspChannel();

		Fibonacci f = new Fibonacci(c1);
		f.start();
		for(int i = 0; i<10; i++)
			System.out.println(c1.read());
		
		System.exit(0);
		
	}
}
