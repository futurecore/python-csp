package JyCSP;

public interface JyCspTimerGuardInterface {
	
	public void setAlarm(long duration);
	public boolean isSelectable();
	public long read();
	public void sleep(long duration);
	public void enable();
	public void disable();
	public void select();
}
