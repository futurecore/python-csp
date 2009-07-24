package JyCSP.builtins;

import JyCSP.Alt;
import JyCSP.JavaCspChannel;
import JyCSP.JavaCspProcess;

public class Multi extends JavaCspProcess {
	
	private JavaCspChannel cin0;

	private JavaCspChannel cin1;

	private JavaCspChannel cout;

	public Multi(JavaCspChannel cin0, JavaCspChannel cin1, JavaCspChannel cout) {
		super();
		this.cin0 = cin0;
		this.cin1 = cin1;
		this.cout = cout;
	}

	@Override
	public void target() {
		
		while (true) {

			this.cout.write(((Integer)cin0.read()) * ((Integer)cin1.read()));
		}
	}
}
