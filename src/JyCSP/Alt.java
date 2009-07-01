package JyCSP;

import org.python.core.*;

public class Alt extends PyObject implements JyCspAltInterface{
	
	protected JyCspAltInterface jcsi;
	
	public Alt(JavaCspChannel...args){
		super();
		this.jcsi = CspFactory.createJavaCspAlt(args);
	}

	public void poison(){
		this.jcsi.poison();
	}
	
	public Object preselect(){
		return this.jcsi.preselect();
	}
	
	public Object select(){
		return this.jcsi.select();
	}
	
	public Object fair_select(){
		return this.jcsi.fair_select();
	}
	
	public Object last_selected(){
		return this.jcsi.last_selected();
	}
	
	public boolean hasNext(){
		return this.jcsi.hasNext();
	}

	@Override
	public int getGuardLength() {
		return this.jcsi.getGuardLength();
	}

}
