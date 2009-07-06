package JyCSP;

import org.python.core.*;

/**
 * 
 * @author Sam Wilson, Sarah Mount
 * @version 1.0
 * 
 *  Java representation of the Jython Class ALT.
 * 
 * 
 * 
 */
public class Alt extends PyObject implements JyCspAltInterface {

	/**
	 * Java ALT Interface for the Jython Class ALT.
	 */
	protected JyCspAltInterface jcsi;

	/**
	 * Default Constructor.
	 * Make a Call to the static method createJavaCspAlt in
	 * the CspFactory Class
	 * 
	 * @param args List of Guards for the ALT to Select from.
	 */
	public Alt(JavaCspChannel... args) {
		super();
		this.jcsi = CspFactory.createJavaCspAlt(args);
	}

	/**
	 * Straight through call to Poison method in the Jython Class
	 * 
	 * Causes a Channel to be poisoned, Data can not be sent down 
	 * a poisoned channel.
	 */
	public void poison() {
		this.jcsi.poison();
	}

	/**
	 * Straight through call to pri_select method in the Jython Class
	 * 
	 * Select a guard to synchronise with, in order of
     * "priority". The guard with the lowest index in the guards
     * list has the highest priority
	 */
	public Object pri_select() {
		return this.jcsi.pri_select();
	}

	/**
	 * Straight through call to the select method in the Jython Class
	 * 
	 * Randomly select from ready guards.
	 * 
	 */
	public Object select() {
		return this.jcsi.select();
	}

	/**
	 * Straight through call to the fair_select method in the Jython Class
	 * 
	 * Select a guard to synchronise with. Do not select the
     * previously selected guard (unless it is the only guard
     * available).
	 */
	public Object fair_select() {
		return this.jcsi.fair_select();
	}

	/**
	 * Allow access to the Jython variable.
	 * 
	 * @return last selected Channel from this ALT
	 */
	public Object last_selected() {
		return this.jcsi.last_selected();
	}

	/**
	 * Allows access to the list of guards within the Jython Class
	 * 
	 * @return true if the list of guards is greater than 0
	 * 				false otherwise
	 */
	public boolean hasNext() {
		return this.jcsi.hasNext();
	}

	/**
	 * Allows access to list of guards within the Jython Class
	 * 
	 * @return int representing the number of guards in this ALT
	 */
	public int getGuardLength() {
		return this.jcsi.getGuardLength();
	}

}
