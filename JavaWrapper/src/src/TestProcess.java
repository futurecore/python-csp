import JyCSP.*;
import org.python.core.PyString;

public class TestProcess extends JavaCspProcess{

	public JavaCspChannel c;
	
	public TestProcess(){
		super();
	}
	
	public void target() {
			System.out.println("Hello world! from " + this.getPid());		
	}


}
