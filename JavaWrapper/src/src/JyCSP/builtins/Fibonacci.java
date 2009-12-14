package JyCSP.builtins;

import JyCSP.*;

public class Fibonacci extends JavaCspProcess {
	
	private JavaCspChannel cout;
	
	public Fibonacci(JavaCspChannel cout){
		super();
		this.cout = cout;
	}

	@Override
	public void target() {
		int a_int = 1;
		int b_int = 1;
		cout.write(0);
		    while(true){
		        cout.write(a_int);
		        int c = a_int;
		        a_int = b_int;
		        b_int = c + b_int;		    
		    }
	}

}
