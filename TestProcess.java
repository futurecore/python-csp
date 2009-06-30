import JyCSP.*;
import org.python.core.PyString;

public class TestProcess extends JavaCspProcess{

	public JCspChannel c;
	
	public void target() {
			//System.out.println("Hello world! from " + this.getPid());
			this.c = new JCspChannel();
			c.write(new PyString("Hello world! from " + this.getPid()));
			
			
	}


}
