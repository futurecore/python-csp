package JyCSP.builtins;

import JyCSP.*;

public class Blackhole extends JavaCspProcess {
	
	private JavaCspChannel cin;
	
	public Blackhole(JavaCspChannel cin){
		super();
		this.cin = cin;
	}

	@Override
	public void target() {
		while(true){
			this.cin.read();
		}
	}

}
