package JyCSP;

public class JavaCspProcess implements JavaCspProcessInterface{
	
	protected JyCspProcessInterface jcpi;
	
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

	@Override
	public void target() {	
	}

}
