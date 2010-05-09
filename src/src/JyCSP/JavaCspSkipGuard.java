package JyCSP;

import org.python.core.PyObject;

import JyCSP.Interfaces.JyCspSkipGuardInterface;
import JyCSP.util.CspFactory;

public class JavaCspSkipGuard extends PyObject implements JyCspSkipGuardInterface{
	
	/**
	 * Java Process Interface for the Jython Class JycspProcess.
	 */
	protected JyCspSkipGuardInterface jcpi;
	
	/**
	 * Required for nesting
	 */
	public Object name = new Object();
	
	
	/**
	 * Default constructor
	 */
	public JavaCspSkipGuard(){
		super();
		this.jcpi = CspFactory.createJavaCspSkipGuard();
	}


	@Override
	public void disable() {
		this.jcpi.disable();
	}


	@Override
	public void enable() {
		this.jcpi.enable();
	}


	@Override
	public boolean is_selectable() {
		return this.jcpi.is_selectable();
	}


	@Override
	public Object select() {
		return this.jcpi.select();
	}
}
