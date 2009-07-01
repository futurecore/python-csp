package JyCSP;

public interface JyCspProcessInterface {
	
	public void start();
	public void run();
	public void sleep(int t);
	public long getPid();
	public void join(long t);
	public void join();
}
