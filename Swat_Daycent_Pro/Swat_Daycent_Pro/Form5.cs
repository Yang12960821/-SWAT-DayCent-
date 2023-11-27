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
    public partial class Form5 : Form
    {
        public Form5()
        {
            InitializeComponent();
        }

        private void button1_Click(object sender, EventArgs e)
        {
            string text = "";
            if (checkBox1.Checked)
            {
                text += "SYLD/t/ha,";
            }
            if (checkBox2.Checked)
            {
                text += "ORGN/kg/ha,";
            }
            if (checkBox3.Checked)
            {
                text += "PCP/mm,";
            }
            if (checkBox4.Checked)
            {
                text += "SNOMELT/mm,";
            }
            if (checkBox5.Checked)
            {
                text += "PET/mm,";
            }
            if (checkBox6.Checked)
            {
                text += "ET/mm,";
            }
            if (checkBox7.Checked)
            {
                text += "SW/mm,";
            }
            if (checkBox8.Checked)
            {
                text += "PERC/mm,";
            }
            if (checkBox9.Checked)
            {
                text += "SURQ/mm,";
            }
            if (checkBox10.Checked)
            {
                text += "GW_Q/mm,";
            }
            if (checkBox11.Checked)
            {
                text += "WYLD/mm,";
            }
            if (checkBox12.Checked)
            {
                text += "ORGP/kg/ha,";
            }
            if (checkBox13.Checked)
            {
                text += "NSURQ/kg/ha,";
            }
            if (checkBox14.Checked)
            {
                text += "SOLP/kg/ha,";
            }
            if (checkBox15.Checked)
            {
                text += "SEDP/kg/ha,";
            }
            if (checkBox16.Checked)
            {
                text += "LATQ/mm,";
            }
            if (checkBox17.Checked)
            {
                text += "LATNO3/kg/ha,";
            }
            if (checkBox18.Checked)
            {
                text += "GWNO3/kg/ha,";
            }
            if (checkBox19.Checked)
            {
                text += "CHOLA/mic/L,";
            }
            if (checkBox20.Checked)
            {
                text += "CBODU/mg/L,";
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
