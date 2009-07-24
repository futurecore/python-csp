package JyCSP.builtins;

import JyCSP.JavaCspChannel;
import JyCSP.JavaCspProcess;

public class Prefix<T> extends JavaCspProcess{

	private JavaCspChannel cin;
	
	private JavaCspChannel cout;
	
	private T prefix_item;
	
	public Prefix(JavaCspChannel cin, JavaCspChannel cout, T PrefixItem){
		super();
		this.cin = cin;
		this.cout = cout;
		this.prefix_item = PrefixItem;
		
	}

	@Override
	public void target() {
		T pre = this.prefix_item;
		while(true){
			this.cout.write(pre);
			pre = (T) cin.read();
		}
	}

}
