package JyCSP.builtins;

import JyCSP.JavaCspChannel;
import JyCSP.JavaCspProcess;

public class Zeroes extends JavaCspProcess {
	
	private JavaCspChannel chnl;
	
	
	public Zeroes(JavaCspChannel chnl){
		super();
		this.chnl = chnl;
	}

	@Override
	public void target() {
		while(true){
			this.chnl.write(0);
		}
		
	}

}
