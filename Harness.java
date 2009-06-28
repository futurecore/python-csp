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
		Par p = new Par(t, t1);
		/*JCspChannel c1 = new JCspChannel();
		JCspChannel c2 = new JCspChannel();
		JCspChannel c3 = new JCspChannel();
		JCspChannel c4 = new JCspChannel();
		JCspChannel c5 = new JCspChannel();*/
		// c.write("HELLO");
		p.start();
		Alt a = new Alt(t.c,t1.c);
		System.out.println(a.select());
		

	}

}
