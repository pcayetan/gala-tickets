package djamelfel.gala;

import android.app.ActionBar;
import android.content.Intent;
import android.database.MatrixCursor;
import android.os.Bundle;
import android.support.v7.app.ActionBarActivity;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.EditText;
import android.widget.ListView;
import android.widget.SimpleCursorAdapter;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.Iterator;

public class Settings extends ActionBarActivity implements View.OnClickListener {
    private ArrayList<Key_List> key_list;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);

        Intent intent = getIntent();
        if (intent != null) {
            Log.i("intent", "variable");
            key_list = intent.getParcelableArrayListExtra("key_list");
        }
        if (key_list != null) {
            updateView();
        } else {
            key_list = new ArrayList<Key_List>();
        }
        findViewById(R.id.new_key).setOnClickListener(this);
     }

    @Override
    public void onClick(View v) {
        switch (v.getId()){
            case R.id.new_key:
                EditText id = (EditText)findViewById(R.id.id);
                EditText key = (EditText)findViewById(R.id.key);

                String idS = id.getText().toString();
                String keyS = key.getText().toString();

                if (idS.isEmpty() || keyS.isEmpty()) {
                    Toast.makeText(getApplicationContext(), R.string.empty_text_area, Toast
                            .LENGTH_LONG).show();
                }
                else {
                    key_list.add(new Key_List(Integer.parseInt(idS), keyS));
                    id.setText("");
                    key.setText("");
                    updateView();
                }
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        ActionBar actionBar = getActionBar();
        if (actionBar != null) {
            actionBar.setDisplayHomeAsUpEnabled(true);
        }
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            case android.R.id.home:
                Intent intent = new Intent(Settings.this, Read_QR_Code.class);
                intent.putParcelableArrayListExtra("key_list", key_list);
                startActivity(intent);
                return true;
            default:
                return super.onOptionsItemSelected(item);
        }
    }

    public void updateView() {
        String[] columns = new String[]{"_id", "id", "key"};
        MatrixCursor matrixCursor = new MatrixCursor(columns);

        startManagingCursor(matrixCursor);

        Iterator<Key_List> itr = key_list.iterator();
        while(itr.hasNext()) {
            Key_List kl = itr.next();
            matrixCursor.addRow(new Object[]{
                    0, kl.getId(), kl.getKey()
            });
        }

        String[] from = new String[]{"id", "key"};
        int[] to = new int[]{R.id.textViewCol1, R.id.textViewCol2};

        SimpleCursorAdapter adapter = new SimpleCursorAdapter(this, R.layout.row_item,
                matrixCursor, from, to, 0);

        ListView lv = (ListView) findViewById(R.id.listView);
        lv.setAdapter(adapter);
    }
}
