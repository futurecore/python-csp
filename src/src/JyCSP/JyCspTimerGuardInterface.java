package JyCSP;

public interface JyCspTimerGuardInterface {
	
	public void set_alarm(long duration);
	public boolean is_selectable();
	public long read();
	public void sleep(long duration);
	public void enable();
	public void disable();
	public void select();
	public long get_alarm();
}
