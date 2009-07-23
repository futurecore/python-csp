package JyCSP.Interfaces;

public interface JyCspProcessInterface {
	
	public void start();
	public void run();
	public void sleep(int t);
	public long getPid();
	public Thread.State getState();
	public void join();
	public void join(long duration);
}
