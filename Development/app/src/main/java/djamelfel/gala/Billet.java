package djamelfel.gala;

import android.os.Parcel;
import android.os.Parcelable;

import java.io.Serializable;

/**
 * Created by djamel on 08/11/15.
 */
public class Billet implements Serializable, Parcelable{
    private String id_billet;
    private int quantity;
    private int prod_validate;

    public Billet(String id_billet, int quantity) {
        this.id_billet = id_billet;
        this.quantity = quantity;
        this.prod_validate = 1;
    }

    public Billet(String save) {
        String[] str = save.split(" ");
        this.id_billet = str[0];
        this.quantity = Integer.parseInt(str[1]);
        this.prod_validate = Integer.parseInt(str[2]);
    }

    protected Billet(Parcel in) {
        this.id_billet = in.readString();
        this.quantity = in.readInt();
        this.prod_validate = in.readInt();
    }

    public String getId_billet() {
        return this.id_billet;
    }

    public void validatePlace() {
        this.prod_validate++;
    }

    public boolean isClickable() {
        if(this.quantity < this.prod_validate)
            return true;
        return false;
    }

    @Override
    public int describeContents() {
        return 0;
    }

    public String writeToFile() {
        return id_billet + " " + String.valueOf(quantity) + " " + String.valueOf(prod_validate);
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeString(this.id_billet);
        dest.writeInt(this.quantity);
        dest.writeInt(this.prod_validate);
    }

    public static final Creator<Billet> CREATOR = new Creator<Billet>() {
        @Override
        public Billet createFromParcel(Parcel in) {
            return new Billet(in);
        }

        @Override
        public Billet[] newArray(int size) {
            return new Billet[size];
        }
    };
}
