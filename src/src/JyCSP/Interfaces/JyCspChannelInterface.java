package JyCSP.Interfaces;

public interface JyCspChannelInterface {

	public void write(Object o);
	public Object read();
	public void poison();
	public Object select();
	public void disable();
	public void enable();
	public boolean is_selected();
	public boolean is_selectable();
	
}
