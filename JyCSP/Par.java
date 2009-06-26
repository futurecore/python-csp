package JyCSP;

public class Par implements JyCspParInterface {

	protected JyCspParInterface jcpi;
	
	public Par(JavaCspProcess...args){
		super();
		this.jcpi = CspFactory.createJavaCspPar(args);
	}

	@Override
	public void run() {
		this.jcpi.run();
	}

	@Override
	public void start() {
		this.jcpi.start();
	}

	@Override
	public void stop() {
		this.jcpi.stop();
	}
}
