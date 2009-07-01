package JyCSP;

import org.python.core.*;
import org.python.core.PyObject;

public class JavaCspChannel extends PyObject implements JyCspChannelInterface{
	
	protected JyCspChannelInterface jcsi;
	
	public String name;
	

	public JavaCspChannel(){
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
	
	public boolean is_selectable(){
		return this.jcsi.is_selectable();
	}


}
