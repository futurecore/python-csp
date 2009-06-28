import JyCSP.*;


public class TestProcess extends JavaCspProcess{

	public JCspChannel c;
	
	public void target() {
			//System.out.println("Hello world! from " + this.getPid());
			this.c = new JCspChannel();
			c.write("Hello world! from " + this.getPid());
	}


}
