package JyCSP.builtins;

import JyCSP.*;

public class Id extends JavaCspProcess {
	
	private JavaCspChannel cin;
	
	private JavaCspChannel cout;
	
	public Id(JavaCspChannel cin, JavaCspChannel cout){
		super();
		this.cin = cin;
		this.cout = cout;
		
	}

	@Override
	public void target() {
		while(true){
			this.cout.write(cin.read());
		}
	}

}
