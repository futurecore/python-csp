package JyCSP.builtins;

import JyCSP.*;

public class Succ extends JavaCspProcess{

	private JavaCspChannel cin;
	
	private JavaCspChannel cout;
	
	public Succ(JavaCspChannel cin, JavaCspChannel cout){
		super();
		this.cin = cin;
		this.cout = cout;
		
	}

	@Override
	public void target() {
		while(true){
			this.cout.write(((Integer)cin.read()) + 1);
		}
	}
}
