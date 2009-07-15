package JyCSP;

import org.python.core.PyObject;

public class TimerGuard extends PyObject implements JyCspTimerGuardInterface{

	/**
	 * Java Timer Guard Interface for the Jython Class TimerGuard.
	 */
	protected JyCspTimerGuardInterface jcsi;
	
	/**
	 * Name of the Guard
	 */
	public String name;

	/**
	 */
	public TimerGuard() {
		super();
		this.jcsi = CspFactory.createJavaCspTimerGuard();
	}

	@Override
	public void disable() {
		this.jcsi.disable();
	}

	@Override
	public void enable() {
		this.jcsi.enable();

	}

	@Override
	public boolean is_selectable() {
		return this.jcsi.is_selectable();
	}

	@Override
	public long read() {
		return this.jcsi.read();
	}

	@Override
	public void select() {
		this.jcsi.select();

	}

	@Override
	public void set_alarm(long duration) {
		this.jcsi.set_alarm(duration);
	}

	@Override
	public void sleep(long duration) {
		this.jcsi.sleep(duration);

	}

	public long get_alarm() {
		return this.jcsi.get_alarm();
	}
	

}
