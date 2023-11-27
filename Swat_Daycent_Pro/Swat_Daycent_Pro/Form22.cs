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
    public partial class Form22 : Form
    {
        public Form22()
        {
            InitializeComponent();
        }
        int flag;
        private void button1_Click(object sender, EventArgs e)
        {
            if (checkBox1.Checked)
            {
                flag = 1;
            }
            else
            {
                flag = 0;
            }

            if (textBox1.Text.Contains("\\"))
            {
                textBox1.Text = textBox1.Text.Replace("\\", "/");
            }
            if (textBox2.Text.Contains("\\"))
            {
                textBox2.Text = textBox2.Text.Replace("\\", "/");
            }
            if (textBox3.Text.Contains("\\"))
            {
                textBox3.Text = textBox3.Text.Replace("\\", "/");
            }
            if (textBox4.Text.Contains("\\"))
            {
                textBox4.Text = textBox4.Text.Replace("\\", "/");
            }
            if (textBox5.Text.Contains("\\"))
            {
                textBox5.Text = textBox5.Text.Replace("\\", "/");
            }
            if (textBox6.Text.Contains("\\"))
            {
                textBox6.Text = textBox6.Text.Replace("\\", "/");
            }
            if (textBox7.Text.Contains("\\"))
            {
                textBox7.Text = textBox7.Text.Replace("\\", "/");
            }
            if (textBox8.Text.Contains("\\"))
            {
                textBox8.Text = textBox8.Text.Replace("\\", "/");
            }


            Form1 lForm1 = (Form1)this.Owner;//把Form2的父窗口指针赋给lForm1
            lForm1.Stroutdir = textBox6.Text;
            lForm1.StrValue = textBox1.Text + " " + textBox2.Text + " " + textBox3.Text + " " + textBox4.Text + " " + textBox5.Text + " " + textBox6.Text + " " + textBox7.Text + " " + textBox8.Text+ " " + flag;//使用父窗口指针赋值
            this.Close();
        }
    }
}
