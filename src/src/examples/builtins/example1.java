package examples.builtins;

import JyCSP.*;
import JyCSP.builtins.*;

public class example1 {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		JavaCspChannel c1 = new JavaCspChannel();
		JavaCspChannel c2 = new JavaCspChannel();
		
		Succ s = new Succ(c1,c2);
		s.start();
		c1.write(0);
		while(true){
			int i = (Integer) c2.read();
			System.out.println(i);
			if(i == 10000){
				System.exit(0);
			}

			c1.write(i);
		}
		
	}

}
