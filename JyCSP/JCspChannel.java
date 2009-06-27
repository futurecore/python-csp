package JyCSP;

public class JCspChannel implements JyCspChannelInterface{
	
	protected JyCspChannelInterface jcsi;
	
	public JCspChannel(){
		super();
		this.jcsi = CspFactory.createJavaCspChannel();
	}

	public void write(Object o){
		this.jcsi.write(o);
	}
	
	public Object read(){
		return this.jcsi.read();
	}
	
	public void poison(){
		this.jcsi.poison();
	}
	
	public Object select(){
		return this.jcsi.select();
	}
	
	public void disable(){
		this.jcsi.disable();
	}
	
	public void enable(){
		this.jcsi.enable();
	}
	
	public boolean is_selected(){
		return this.jcsi.is_selected();
	}


}
