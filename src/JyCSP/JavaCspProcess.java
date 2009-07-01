package JyCSP;

import org.python.core.*;

public class JavaCspProcess extends PyObject implements JavaCspProcessInterface{
	
	protected JyCspProcessInterface jcpi;
	
	public Object enclosing;
	
	public JavaCspProcess(){
		super();
		this.jcpi = CspFactory.createJavaCspProcess(this);
	}
	
	public void start(){
		this.jcpi.start();
	}
	
	public void run(){
		this.jcpi.run();
	}
	
	public void sleep(int t){
		this.jcpi.sleep(t);
	}
	
	public long getPid(){
		return this.jcpi.getPid();
	}
	
	public void join(long t){
		this.jcpi.join(t);
	}
	
	public void join(){
		this.jcpi.join();
	}

	@Override
	public void target() {	
	}

}
