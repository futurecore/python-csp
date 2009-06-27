import JyCSP.CspFactory;
import JyCSP.*;


public class Harness {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		TestProcess t = new TestProcess();
		TestProcess t1 = new TestProcess();
		System.out.println(t1.getPid());
		Seq s = new Seq(t1,t);
		JCspChannel c = new JCspChannel();
		c.write("HELLO");
		s.start();
		
		

	}

}
