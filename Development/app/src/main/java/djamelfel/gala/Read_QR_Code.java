package djamelfel.gala;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ActivityNotFoundException;
import android.content.DialogInterface;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.support.v7.app.ActionBarActivity;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import android.widget.Toast;

import java.io.UnsupportedEncodingException;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Iterator;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;


public class Read_QR_Code extends ActionBarActivity {

    static final String ACTION_SCAN = "com.google.zxing.client.android.SCAN";
    private ArrayList<Key_List> key_list;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_read__qr__code);

        Intent intent = getIntent();
        if (intent != null) {
            key_list = intent.getParcelableArrayListExtra("key_list");
        }
    }

    public void scanQR(View v) {
        if (key_list == null) {
            display(getString(R.string.error_lib_empty), false);
            return;
        }
        try {
            Intent intent = new Intent(ACTION_SCAN);
            intent.putExtra("SCAN_MODE", "QR_CODE_MODE");
            startActivityForResult(intent, 0);
        } catch (ActivityNotFoundException anfe) {
            showDialog(Read_QR_Code.this, "Auncun lecteur de QRCode n'a été trouvé", "Télécharger" +
                    " un scanner ?", "Oui", "Non").show();
        }
    }

    private static AlertDialog showDialog(final Activity act, CharSequence title, CharSequence
            message, CharSequence buttonYes, CharSequence buttonNo) {
        AlertDialog.Builder downloadDialog = new AlertDialog.Builder(act);
        downloadDialog.setTitle(title);
        downloadDialog.setMessage(message);
        downloadDialog.setPositiveButton(buttonYes, new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialogInterface, int i) {
                Uri uri = Uri.parse("market://search?q=pname:" + "com.google.zxing.client.android");
                Intent intent = new Intent(Intent.ACTION_VIEW, uri);
                try {
                    act.startActivity(intent);
                } catch (ActivityNotFoundException anfe) {

                }
            }
        });
        downloadDialog.setNegativeButton(buttonNo, new DialogInterface.OnClickListener() {
            public void onClick(DialogInterface dialogInterface, int i) {
            }
        });
        return downloadDialog.show();
    }

    public void onActivityResult(int requestCode, int resultCode, Intent intent) {
        if (requestCode == 0) if (resultCode == RESULT_OK) {
            String contents = intent.getStringExtra("SCAN_RESULT");

            validateTicket(contents);
        }
    }

    public void validateTicket(String result) {
        String str[] = result.split(" ");
        Boolean found = false;

        Iterator<Key_List> itr = key_list.iterator();
        while (itr.hasNext()) {
            Key_List key = itr.next();
            if (key.getId() == Integer.parseInt(str[1])) {
                String hmac = hmacDigest(str[0] + " " + str[1] + " " + str[2], key.getKey(),
                        "HmacSHA1");
                if(str[3].equals(hmac.substring(0, 8).toUpperCase())) {
                    display(getString(R.string.ebillet_true), true);
                    found = true;
                }
                return;
            }
        }
        if (!found) {
            display(getString(R.string.ebillet_false), false);
        }
    }

    public void display(String msg, boolean success) {
        LayoutInflater inflater = getLayoutInflater();
        View layout;
        if(success) {
            layout = inflater.inflate(R.layout.toast_success,
                    (ViewGroup) findViewById(R.id.toast_success));
        }
        else {
            layout = inflater.inflate(R.layout.toast_failure,
                    (ViewGroup) findViewById(R.id.toast_failure));
        }
        TextView text = (TextView)layout.findViewById(R.id.text);
        text.setTextSize(20);
        text.setText(msg.toUpperCase());

        Toast toast = new Toast(getApplicationContext());
        toast.setDuration(Toast.LENGTH_LONG);
        toast.setView(layout);
        toast.show();
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        super.onCreateOptionsMenu(menu);
        getMenuInflater().inflate(R.menu.menu_read__qr__code, menu);

        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();

        if (id == R.id.action_settings) {
            Intent intent = new Intent(Read_QR_Code.this, Settings.class);
            if (key_list != null)
                if (!key_list.isEmpty())
                    intent.putParcelableArrayListExtra("key_list", key_list);
            startActivity(intent);
            return true;
        }

        return super.onOptionsItemSelected(item);
    }

    public static String hmacDigest(String msg, String keyString, String algo) {
        String digest = null;
        try {
            SecretKeySpec key = new SecretKeySpec((keyString).getBytes("UTF-8"), algo);
            Mac mac = Mac.getInstance(algo);
            mac.init(key);

            byte[] bytes = mac.doFinal(msg.getBytes("ASCII"));

            StringBuffer hash = new StringBuffer();
            for (int i = 0; i < bytes.length; i++) {
                String hex = Integer.toHexString(0xFF & bytes[i]);
                if (hex.length() == 1) {
                    hash.append('0');
                }
                hash.append(hex);
            }
            digest = hash.toString();
        } catch (UnsupportedEncodingException e) {
        } catch (InvalidKeyException e) {
        } catch (NoSuchAlgorithmException e) {
        }
        return digest;
    }
}
