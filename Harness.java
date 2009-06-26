import JyCSP.CspFactory;
import JyCSP.Par;


public class Harness {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		TestProcess t = new TestProcess();
		TestProcess t1 = new TestProcess();
		Par p = new Par(t,t1);
		p.start();
		
		

	}

}
