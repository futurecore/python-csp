package JyCSP;

public class TimerGuard implements JyCspTimerGuardInterface {

	/**
	 * Java Timer Guard Interface for the Jython Class TimerGuard.
	 */
	protected JyCspTimerGuardInterface jcsi;

	/**
	 * Default Constructor. Make a Call to the static method createJavaCspAlt in
	 * the CspFactory Class
	 * 
	 * @param args
	 *            List of Guards for the ALT to Select from.
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
	public boolean isSelectable() {
		return this.jcsi.isSelectable();
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
	public void setAlarm(long duration) {
		this.jcsi.setAlarm(duration);
	}

	@Override
	public void sleep(long duration) {
		this.jcsi.sleep(duration);

	}

}
