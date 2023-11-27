using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace Swat_Daycent_Pro
{
    public partial class Form6 : Form
    {
        public Form6()
        {
            InitializeComponent();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            string text = "";
            if (checkBox1.Checked)
            {
                text += "FLOW_OUT/cms,";
            }
            if (checkBox2.Checked)
            {
                text += "SED_OUT/tons,";
            }
            if (checkBox3.Checked)
            {
                text += "EVAP/cms,";
            }
            if (checkBox4.Checked)
            {
                text += "TLOSS/cms,";
            }
            if (checkBox5.Checked)
            {
                text += "SEDCONC/mg/kg,";
            }
            if (checkBox6.Checked)
            {
                text += "ORGN_OUT/kg,";
            }
            if (checkBox7.Checked)
            {
                text += "ORGP_OUT/kg,";
            }
            if (checkBox8.Checked)
            {
                text += "NO3_OUT/kg,";
            }
            if (checkBox9.Checked)
            {
                text += "NH4_OUT/kg,";
            }
            if (checkBox10.Checked)
            {
                text += "NO2_OUT/kg,";
            }
            if (checkBox11.Checked)
            {
                text += "MINP_OUT/kg,";
            }
            if (checkBox12.Checked)
            {
                text += "CHLA_OUT/kg,";
            }
            if (checkBox13.Checked)
            {
                text += "CBOD_OUT/kg,";
            }
            if (checkBox14.Checked)
            {
                text += "DISOX_IN/kg,";
            }
            if (checkBox15.Checked)
            {
                text += "DISOX_OUT/kg,";
            }
            if (checkBox16.Checked)
            {
                text += "SOLPST_OUT/mg,";
            }
            if (checkBox17.Checked)
            {
                text += "SORPST_OUT/mg,";
            }
            if (checkBox18.Checked)
            {
                text += "REACTPST/mg,";
            }
            if (checkBox19.Checked)
            {
                text += "VOLPST/mg,";
            }
            if (checkBox20.Checked)
            {
                text += "SETTLPST/mg,";
            }
            Form1 lForm1 = (Form1)this.Owner;//把Form2的父窗口指针赋给lForm1
            //lForm1.Stroutdir = textBox3.Text;
            if (text.Length != 0)
            {
                text = text.Remove(text.Length - 1, 1);
            }

            lForm1.StrValue = text;//使用父窗口指针赋值
            this.Close();
        }
    }
}
